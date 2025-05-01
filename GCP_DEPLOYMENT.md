# ☁️ Deploying Dev.to MCP Server on Google Cloud Run

This guide provides step-by-step instructions for deploying the Dev.to MCP Server on Google Cloud Run.

---

## 📚 Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Set Up Environment Variables](#step-1-set-up-environment-variables)
- [Step 2: Build and Test Locally](#step-2-build-and-test-locally)
- [Step 3: Set Up Google Cloud Project](#step-3-set-up-google-cloud-project)
- [Step 4: Build and Push the Docker Image](#step-4-build-and-push-the-docker-image)
- [Step 5: Deploy to Google Cloud Run](#step-5-deploy-to-google-cloud-run)
- [Step 6: Access Your Deployed Service](#step-6-access-your-deployed-service)
- [Client Authentication](#client-authentication)
- [Step 7: Configure Environment Variables (Optional)](#step-7-configure-environment-variables-optional)
- [Step 8: Set Up Continuous Deployment (Optional)](#step-8-set-up-continuous-deployment-optional)
- [Troubleshooting](#troubleshooting)

---

## ✅ Prerequisites

- Google Cloud Platform account with billing enabled
- Google Cloud SDK installed and configured locally
- Docker installed locally (for building and testing)
- **Optional:** Default Dev.to API key as fallback

---

## 1️⃣ Step 1: Set Up Environment Variables

Create a `.env` file for local development:

```env
# Optional fallback API key, only used when clients don't provide their own
DEVTO_API_KEY=your_api_key_here
```

> **Note:**
> - Never commit this file to version control!
> - The server API key is optional and only used as a fallback when clients don't provide their own.
> - Each client should provide their own API key in their requests.

---

## 2️⃣ Step 2: Build and Test Locally

Before deploying to Google Cloud Run, test the Docker container locally:

```bash
docker-compose up --build

# Test with curl
curl http://localhost:8000/health

# Test with client API key
curl -H "devto-api-key: your_personal_api_key" http://localhost:8000/sse
```

---

## 3️⃣ Step 3: Set Up Google Cloud Project

If you haven't already, create a new project or select an existing one:

```bash
# Create a new project
gcloud projects create [PROJECT_ID] --name="Dev.to MCP Server"

# Set as default project
gcloud config set project [PROJECT_ID]
```

Enable necessary APIs:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## 4️⃣ Step 4: Build and Push the Docker Image

Build and push the Docker image to Google Container Registry:

```bash
gcloud builds submit --tag gcr.io/[PROJECT_ID]/dev-to-mcp:latest .
```

---

## 5️⃣ Step 5: Deploy to Google Cloud Run

Deploy the container to Google Cloud Run:

```bash
gcloud run deploy dev-to-mcp \
  --image gcr.io/[PROJECT_ID]/dev-to-mcp:latest \
  --platform managed \
  --region [REGION] \
  --allow-unauthenticated \
  --set-env-vars "DEVTO_API_KEY=[OPTIONAL-DEFAULT-API-KEY]"
```

Replace:
- `[REGION]` with your preferred Google Cloud region (e.g., `us-central1`)
- `[OPTIONAL-DEFAULT-API-KEY]` with your default API key (optional)

> **Note:** This default API key is only used as a fallback when clients don't provide their own API key.

---

## 6️⃣ Step 6: Access Your Deployed Service

After successful deployment, Google Cloud Run will provide a URL for your service:

```text
Service [dev-to-mcp] revision [dev-to-mcp-00001-example] has been deployed and is serving 100 percent of traffic.
Service URL: https://dev-to-mcp-abcdefg123-uc.a.run.app
```

You can access the SSE endpoint at:
```
https://dev-to-mcp-abcdefg123-uc.a.run.app/sse
```

---

## 🔐 Client Authentication

When connecting to the deployed MCP server, clients need to provide their own Dev.to API key:

```python
# Python example
from fastmcp.transports.sse import SSEClient

# Connect with API key in header
client = SSEClient(
    "https://dev-to-mcp-abcdefg123-uc.a.run.app/sse",
    headers={"devto-api-key": "client_api_key_here"}
)

# Or API key in parameters for specific operations
result = await client.call(
    "create_article",
    {
        "title": "My Article",
        "body_markdown": "# Content",
        "api_key": "client_api_key_here" 
    }
)
```

This ensures that all operations happen under the client's own Dev.to account.

---

## 7️⃣ Step 7: Configure Environment Variables (Optional)

To update environment variables after deployment:

```bash
gcloud run services update dev-to-mcp \
  --set-env-vars "DEVTO_API_KEY=[NEW-OPTIONAL-DEFAULT-API-KEY]"
```

---

## 8️⃣ Step 8: Set Up Continuous Deployment (Optional)

For continuous deployment with GitHub:

1. Connect your GitHub repository to Google Cloud Build
2. Create a build trigger for automatic deployments

See the [Google Cloud Build documentation](https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github) for detailed steps.

---

## 🛠️ Troubleshooting

### 📄 Check Container Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dev-to-mcp" --limit 50
```

### 🧪 Test MCP Endpoint

Use the following Python script to test your MCP endpoint:

```python
import asyncio
from fastmcp.transports.sse import SSEClient

async def test_mcp():
    # Include your personal Dev.to API key
    headers = {"devto-api-key": "your_api_key_here"}
    
    # Connect to the deployed service
    client = SSEClient("https://dev-to-mcp-abcdefg123-uc.a.run.app/sse", headers=headers)
    await client.initialize()
    
    # Public endpoints don't require authentication
    result = await client.call("get_top_articles", {})
    print(result)
    
    # Authenticated endpoints use your API key
    my_articles = await client.call("get_user_articles", {})
    print(my_articles)

if __name__ == "__main__":
    asyncio.run(test_mcp())
```

### ⚠️ Common Issues

1. **API Key Issues:** Ensure each client is using their own valid Dev.to API key for authenticated operations
2. **Connection Timeouts:** Cloud Run has a default timeout of 5 minutes. If your operations take longer, adjust the timeout settings
3. **Memory Limits:** Default memory allocation might be insufficient for heavy loads
4. **CORS Issues:** If accessing from browser clients, ensure proper CORS headers are configured 