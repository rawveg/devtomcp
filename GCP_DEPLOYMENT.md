# ☁️ Deploying Dev.to MCP Server on Google Cloud Run

This guide provides step-by-step instructions for deploying the Dev.to MCP Server on Google Cloud Run.

---

## 🚦 Choosing a Deployment Mode: REST (OpenAPI) vs SSE (MCP)

The Dev.to MCP Server supports two deployment modes:

| Mode         | Description                                                                 |
|--------------|-----------------------------------------------------------------------------|
| 🟢 SSE/MCP   | For LLM/agent integration, using the Model Context Protocol (MCP)           |
| 🟦 REST/OpenAPI | For direct HTTP access, OpenAPI tool runners, and OpenAI-compatible tools |

### 🌟 **Recommended: REST/OpenAPI Mode**
- **Best for most users and production deployments on Cloud Run**
- Each request is authenticated via an `Authorization: Bearer <API_KEY>` header
- No API key is stored in the container or environment
- Fully compatible with OpenAI, LangChain, and other OpenAPI tool runners
- Easier to secure: no destructive access unless a valid API key is provided per request

#### 🚀 Deploying in REST Mode (Recommended)
```bash
gcloud run deploy devtomcp \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --region [REGION] \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="SERVER_MODE=rest" \
  --set-env-vars="DEVTO_API_BASE_URL=https://dev.to/api" \
  --format="json"
```

### 🟢 SSE/MCP Mode (Agent/LLM Integration)
- For advanced use cases where you need MCP/agent protocol support
- API key is stored in the environment (`DEVTO_API_KEY`)
- **⚠️ Requires strict infrastructure-level security controls!**
- All requests use the same API key, so unauthorized access could be destructive

#### 🚀 Deploying in SSE/MCP Mode
```bash
gcloud run deploy devtomcp \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --region [REGION] \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="DEVTO_API_KEY=your_dev_to_api_key_here" \
  --set-env-vars="SERVER_MODE=sse" \
  --set-env-vars="DEVTO_API_BASE_URL=https://dev.to/api" \
  --format="json"
```

### 🔒 Security Implications
- **REST mode:** Each request must include a valid API key, so destructive access is limited to those with a key. Safer for public endpoints.
- **SSE mode:** All requests use the same API key from the environment. You MUST implement Cloud Run authentication, IAP, or other access controls to prevent unauthorized use.

---

## ✅ Prerequisites

- Google Cloud Platform account with billing enabled
- Google Cloud SDK installed and configured locally

---

## 3️⃣ Step 1: Set Up Google Cloud Project

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

## 2️⃣ Step 2: Deploy to Google Cloud Run

Deploy the container to Google Cloud Run:

```bash
# Build from source
```bash
gcloud run deploy devtomcp \
  --source . \
  --platform managed \
  --allow-unauthenticated \
  --region [REGION] \
  --set-env-vars="LOG_LEVEL=<<LOG_LEVEL>>" \
  --set-env-vars="DEVTO_API_KEY=<<DEVTO_API_KEY>>" \
  --set-env-vars="DEVTO_API_BASE_URL=<<DEVTO_API_BASE_URL>>" \
  --format="json"
```

Replace:
- `[REGION]` with your preferred Google Cloud region (e.g., `us-central1`)
- `<<LOG_LEVEL>>` with your preferred log level (e.g., `INFO`)
- `<<DEVTO_API_KEY>>` with your Dev.to API key
- `<<DEVTO_API_BASE_URL>>` with your Dev.to API base URL (e.g., `https://dev.to/api`)


---

## 2️⃣ Step 3: Access Your Deployed Service

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
client = SSEClient("https://dev-to-mcp-abcdefg123-uc.a.run.app/sse")

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

## ⚠️ **IMPORTANT: Single-User Configuration**
This server is designed for single-user deployment. Your Dev.to API key is stored server-side and all operations will be performed using this key.

## 🔐 Security Requirements

Before deploying this server, you MUST understand and implement appropriate security measures:

1. **API Key Protection**
   - Your Dev.to API key will be stored server-side
   - All operations will use this single API key
   - Unauthorized access could compromise your Dev.to account
   - Regular key rotation is strongly recommended

2. **Required Security Measures**
   - Do NOT deploy without implementing AT LEAST ONE of these security controls:
     1. [Cloud Run Authentication](https://cloud.google.com/run/docs/authenticating/overview)
     2. [Identity-Aware Proxy (IAP)](https://cloud.google.com/iap/docs/cloud-run-tutorial)
     3. [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs/overview)
     4. [Ingress Controls](https://cloud.google.com/run/docs/securing/ingress)

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
    # Connect to the deployed service
    client = SSEClient("https://dev-to-mcp-abcdefg123-uc.a.run.app/sse")
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

## 🔒 Implementing Security Controls

### Option 1: Cloud Run Authentication
```bash
# Remove public access
gcloud run services update dev-to-mcp \
  --no-allow-unauthenticated

# Grant access to specific users/service accounts
gcloud run services add-iam-policy-binding dev-to-mcp \
  --member="user:your-email@example.com" \
  --role="roles/run.invoker"
```

### Option 2: Identity-Aware Proxy (IAP)
1. Set up OAuth consent screen
2. Configure IAP
3. Create OAuth credentials
4. Enable IAP for your Cloud Run service

### Option 3: VPC Service Controls
1. Create a VPC network
2. Configure service perimeter
3. Add Cloud Run service to perimeter
4. Set up authorized networks

### Option 4: Ingress Controls
```bash
# Restrict to internal traffic and load balancers
gcloud run services update dev-to-mcp \
  --ingress=internal-and-cloud-load-balancing
```

## ⚠️ Security Disclaimer

By deploying this server, you acknowledge:
1. This is a single-user server - all operations use your API key
2. You are responsible for implementing proper security controls
3. The maintainers are not liable for unauthorized access or API key misuse
4. Regular security audits and key rotation are your responsibility

## 📚 Additional Resources

- [Cloud Run Security Overview](https://cloud.google.com/run/docs/securing/security-overview)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [IAP Documentation](https://cloud.google.com/iap/docs)
- [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs/overview)