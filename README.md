Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
# Airflow + OpenAI Paper Summarization

This repository contains an Airflow project that demonstrates automated paper summarization using OpenAI/Azure LLMs within Airflow DAGs. It includes example DAGs and helper scripts to run locally (Windows-friendly patches included).

**Quick Links**
- **Project:** Airflow_OPENAI_papersummarization
- **Environment/example file:** [e.env.example](e.env.example)
- **Azure config guide:** [AZURE_SETUP.md](AZURE_SETUP.md)

**Requirements**
- Python 3.8+ (see [requirements.txt](requirements.txt))
- Docker & Docker Compose (for containerized local run)

**Quickstart (local, containerized)**
1. Copy or review environment variables: copy `e.env.example` to `.env` and set your secrets (OpenAI/Azure keys) as needed.
2. Install Python dependencies (optional, for local script runs):

```bash
pip install -r requirements.txt
```

3. Build and start services with Docker Compose:

```bash
docker-compose up --build
```

4. After services start, open Airflow UI at http://localhost:8080/.

Notes:
- If you are on Windows, this project contains `dags/airflow_windows_patch.py` and `dags/airflow_logging_patch.py` to help with Windows-specific behavior. Apply or review the patches before running if needed.

Project layout
--------------
- `dags/` : Airflow DAGs and helper scripts
    - `summarization.py` : Primary DAG implementing paper summarization using the OpenAI/Azure model integration
    - `exampledag.py` : Small example DAG used for testing and demonstration
    - `airflow_windows_patch.py`, `airflow_logging_patch.py` : Windows and logging compatibility helpers
- `include/` : Additional assets (e.g., `paper_summary.txt`, `raw_pdf_text.txt`)
- `plugins/` : Airflow plugins (if any)
- `Dockerfile`, `docker-compose.yml` : Container setup for running Airflow locally
- `load_env.py` : Utility to load environment variables from the example file
- `AZURE_SETUP.md` : Instructions for configuring Azure OpenAI integration
- `requirements.txt` : Python dependencies
- `tests/` : Pytest tests (see `tests/dags/test_dag_example.py`)

Running tests
-------------
Run the unit tests with pytest:

```bash
pytest tests/dags/test_dag_example.py
```

Environment and secrets
-----------------------
- Use `e.env.example` as a template for required environment variables. Keep secrets out of source control.
- See `AZURE_SETUP.md` for Azure-specific configuration steps when using Azure OpenAI.

Developer notes
---------------
- To load environment variables programmatically for local testing, run:

```bash
python load_env.py e.env.example
```

- For Windows-specific Airflow issues, check and apply the Windows patches in `dags/`.

Contributing
------------
Contributions, bug reports and improvements are welcome. Please open issues or PRs describing the change.

Files changed
-------------
- Updated README to reflect repository purpose and quickstart instructions.

If you'd like, I can also run the tests or open a branch with these changes committed. 
