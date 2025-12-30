# Azure OpenAI Setup for Airflow DAG

## Prerequisites

This Airflow DAG (`dags/summarization.py`) requires Azure OpenAI credentials to run the summarization task.

## Step 1: Create Azure OpenAI Resource (if not already done)

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Cognitive Services** resource or **Azure OpenAI** resource
3. Choose region and pricing tier
4. Note the resource name and resource group

## Step 2: Create a Model Deployment

1. In the Azure Portal, go to your Azure OpenAI resource
2. Click **Model deployments** → **Create new deployment**
3. Select a model (e.g., `gpt-35-turbo` or `gpt-4`)
4. Name the deployment (e.g., `gpt35turbo`)
5. Note the deployment name — you'll need this

## Step 3: Get Your Credentials

1. In Azure Portal, go to your resource
2. Click **Keys and Endpoint** (left sidebar)
3. Copy:
   - **Endpoint** — looks like `https://your-resource.openai.azure.com/`
   - **Key 1** or **Key 2** — your API key

## Step 4: Set Environment Variables

Create or update your `e.env` file in the repository root:

```
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_KEY="your-api-key-here"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt35turbo"
```

Replace:
- `your-resource` with your Azure resource name
- `your-api-key-here` with your actual API key
- `gpt35turbo` with your actual deployment name (if different)

## Step 5: Verify Setup (Local Test)

```powershell
# From the repository root, test the env loader
python -c "import load_env; load_env.load_env('e.env'); import os; print('ENDPOINT:', os.environ.get('AZURE_OPENAI_ENDPOINT') is not None); print('KEY:', os.environ.get('AZURE_OPENAI_KEY') is not None)"
```

## Step 6: Run Airflow

Restart the Airflow containers:

```powershell
astro dev restart
```

Then trigger the DAG `paper_summarization_etl_pipeline` from the Airflow Web UI (typically at http://localhost:8080).

## Troubleshooting

### Error: "DeploymentNotFound" or "Resource not found"

- Verify the `AZURE_OPENAI_DEPLOYMENT_NAME` matches exactly the name in Azure Portal
- Verify the resource exists and is in the same region as specified
- Try re-listing deployments in Azure Portal to confirm the deployment is active

### Error: "Unauthorized" or "Invalid API key"

- Double-check `AZURE_OPENAI_KEY` is correct (copy it again from Azure Portal)
- Ensure `AZURE_OPENAI_ENDPOINT` includes the trailing slash

### Environment Variables Not Loading

- Ensure `e.env` is in the repository root (same level as `dags/` and `include/`)
- Check that the file format is correct: `KEY="value"` (one per line)
- Restart the Airflow containers after updating `e.env`

## Example e.env File

```
AZURE_OPENAI_ENDPOINT="https://my-openai-resource.openai.azure.com/"
AZURE_OPENAI_KEY="abcdef1234567890abcdef1234567890"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt35turbo"
OPENAI_API_KEY="not-used-in-dag"
```

## Questions?

Refer to the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/).
