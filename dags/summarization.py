import sys
import os

# Safely import patches that are in the same dags/ directory
try:
    import airflow_windows_patch  # Apply Windows compatibility patch
except ImportError:
    # If patches don't exist, that's okay — continue without them
    pass

try:
    import airflow_logging_patch   # Apply logging configuration patch
except ImportError:
    pass

# Load environment variables from repository root `e.env` (if present)
try:
    import load_env
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    load_env.load_env(os.path.join(_root, '.env'))
except Exception:
    # Best-effort: if loading fails, continue without crashing
    pass
from openai import AzureOpenAI

# Azure OpenAI configuration
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")

import os
import airflow 
from airflow.sdk import Asset, dag, task, get_current_context
import pendulum
import requests
import json
from airflow import DAG
from PyPDF2 import PdfReader
import re
from openai import OpenAI

# Use relative paths that work in both local and Docker environments
DAG_DIR = os.path.dirname(os.path.abspath(__file__))
INCLUDE_DIR = os.path.join(os.path.dirname(DAG_DIR), 'include')
PDF_PATH = os.path.join(INCLUDE_DIR, '2203.02155v1.pdf')
SUMMARY_OUTPUT_PATH = os.path.join(INCLUDE_DIR, 'paper_summary.txt')
RAW_PDF_TEXT_PATH = os.path.join(INCLUDE_DIR, 'raw_pdf_text.txt')
PROCESSED_SECTIONS_PATH = os.path.join(INCLUDE_DIR, 'processed_sections.json')

#API_CONN_ID = 'OPEN_METEO_API'
DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'start_date': pendulum.now('UTC').subtract(days=1)
} 

with DAG(dag_id = 'paper_summarization_etl_pipeline',
         default_args = DEFAULT_ARGS,
         schedule = '@daily',
         catchup = False) as dag:

    @task()  #decorator to define a task
    def read_paper(PDF_PATH: str):
        """
        Task 1: Read the PDF and save raw text to file (avoid XCom serialization).
        """
        if not os.path.exists(PDF_PATH):
            raise FileNotFoundError(f"PDF not found at {PDF_PATH}")

        reader = PdfReader(PDF_PATH)
        pages_text = []

        for page in reader.pages:
            txt = page.extract_text() or ""
            pages_text.append(txt)

        full_text = "\n".join(pages_text)
        
        # Save to file to avoid XCom size limits
        with open(RAW_PDF_TEXT_PATH, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        return 'success'
    
    @task()  #decorator to define a task
    def preprocess_pdf(status: str):
        """
        Task 2: Very simple heuristic-based preprocessing to split text into sections:
        introduction, methods, formulas, conclusion, references.
        """
        # Read from file instead of parameter
        with open(RAW_PDF_TEXT_PATH, 'r', encoding='utf-8') as f:
            text = f.read()

        if not text:
            raise ValueError("No PDF text found")

        lines = [l for l in text.splitlines()]

        # Initialize buckets
        sections = {
            "abstract": [],
            "introduction": [],
            "methods": [],
            "results": [],
            "discussion": [],
            "conclusion": [],
            "references": [],
            "other": [],
        }

        # Regex patterns for headings (very naive, but works for many papers)
        section_patterns = {
            "abstract": re.compile(r"^\s*abstract\b", re.IGNORECASE),
            "introduction": re.compile(r"^\s*introduction\b", re.IGNORECASE),
            "methods": re.compile(
                r"^\s*(materials and methods|methods?|methodology)\b",
                re.IGNORECASE,
            ),
            "results": re.compile(r"^\s*results?\b", re.IGNORECASE),
            "discussion": re.compile(r"^\s*discussion\b", re.IGNORECASE),
            "conclusion": re.compile(r"^\s*conclusions?\b", re.IGNORECASE),
            "references": re.compile(r"^\s*references?\b", re.IGNORECASE),
        }

        current_section = "other"

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Detect section heading
            switched = False
            for name, pattern in section_patterns.items():
                if pattern.match(stripped):
                    current_section = name
                    switched = True
                    break

            # Don't push the heading line twice; if it's a heading,
            # we still keep it inside that section for context.
            sections[current_section].append(stripped)

        # Formulas: naive extraction of lines that look like equations
        formula_lines = []
        formula_pattern = re.compile(
            r"([A-Za-z]\s*=\s*[^=]+)|(\b\d+\s*[\+\-\*/]\s*\d+\b)"
        )
        for line in lines:
            if formula_pattern.search(line):
                formula_lines.append(line.strip())

        # Consolidate into strings
        processed_sections = {
            "abstract": "\n".join(sections["abstract"]).strip(),
            "introduction": "\n".join(sections["introduction"]).strip(),
            "methods": "\n".join(sections["methods"]).strip(),
            "results": "\n".join(sections["results"]).strip(),
            "discussion": "\n".join(sections["discussion"]).strip(),
            "conclusion": "\n".join(sections["conclusion"]).strip(),
            "references": "\n".join(sections["references"]).strip(),
            "formulas": "\n".join(formula_lines).strip(),
        }

        # Save to file to avoid XCom size limits
        with open(PROCESSED_SECTIONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(processed_sections, f, indent=2)
        
        return 'success'

    @task()  #decorator to define a task
    def summarize_with_llm(status: str):
        """
        Task 3: Use Azure OpenAI to summarize the extracted sections.
        Prints and writes summary to a file.
        """
        # Read from file instead of parameter
        with open(PROCESSED_SECTIONS_PATH, 'r', encoding='utf-8') as f:
            sections = json.load(f)

        if not sections:
            raise ValueError("No processed sections found")

        # You can optionally truncate very long texts here to avoid token limits
        # or just rely on model truncation. For a simple example, we just
        # dump the JSON.
        sections_json = json.dumps(sections, indent=2)
        
        client = AzureOpenAI(
            api_key=AZURE_KEY,
            api_version="2025-01-01-preview",
            azure_endpoint=AZURE_ENDPOINT
        )

        system_prompt = (
            "You are an expert research-paper summarization assistant. "
            "You will receive pre-split sections from a PDF: abstract, "
            "introduction, methods, results, discussion, conclusion, formulas, "
            "and references. Produce a concise but detailed summary."
        )

        user_prompt = f"""
            Below is the content of a research paper, already split into major sections.

            Please:
            1. Provide a high-level summary (3–5 bullet points).
            2. Briefly describe the introduction and problem statement.
            3. Summarize the methodology.
            4. Summarize key results and conclusions.
            5. List and briefly interpret the main formulas or equations (if any).
            6. Provide a one-paragraph takeaway for a non-expert audience.

            Sections (JSON):
            {sections_json}
            """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Call Azure OpenAI and handle DeploymentNotFound with guidance (no fallback)
        # Ensure we have a deployment name and endpoint/key configured
        
            # For Azure OpenAI, `model` must be the deployment name (not the model id)
        completion = client.chat.completions.create(
                model="gpt-35-turbo",
                messages=messages,
                temperature=0.7,
            )
        

        summary = completion.choices[0].message.content
        # Print to Airflow logs
        print("\n===== LLM SUMMARY START =====\n")
        print(summary)
        print("\n===== LLM SUMMARY END =====\n")
        # Write to output file
        with open(SUMMARY_OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(summary)

        #ti.xcom_push(key="paper_summary", value=summary)
        return summary

    # Define task dependencies inside the DAG context
    read_result = read_paper(PDF_PATH=PDF_PATH)
    preprocess_result = preprocess_pdf(status=read_result)
    summary = summarize_with_llm(status=preprocess_result)