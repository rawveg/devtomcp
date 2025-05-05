# 🚀 Dev.to MCP Server

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://www.docker.com/)
[![Dev.to API](https://img.shields.io/badge/Dev.to-API-orange?logo=dev.to)](https://developers.forem.com/api)

---

An implementation of a Model Context Protocol (MCP) server for the Dev.to API, providing capabilities for searching, browsing, reading, and creating content on Dev.to.

---

## ✨ Features

| Feature                         | Description                                      |
| ------------------------------- | ------------------------------------------------ |
| 🔍 Browse Latest Articles       | Get the most recent articles from Dev.to          |
| 🌟 Browse Popular Articles      | Get the most popular articles                     |
| 🏷️ Browse by Tag                | Get articles with a specific tag                  |
| 📚 Browse by Title              | Get articles with a specific title                |
| 📖 Read Article                 | Get detailed information about a specific article |
| 👤 User Profile                 | Get information about a Dev.to user               |
| 🔎 Search Articles              | Search for articles using keywords                |
| 👤 Search Articles by User      | Search all articles by a specific user           |
| 📝 Get Article by ID            | Get detailed information about a specific article |
| 📝 Get Article by Title         | Get detailed information about a specific article |
| 🧠 Analyze Article              | Analyze a specific article (prompt-based, summary output)    |
| 🧠 Analyze User Profile         | Analyze a specific user profile (prompt-based, summary output)|
| 📝 Create Article               | Create and publish new articles                   |
| ✏️ Update Article               | Update your existing articles                     |
| 📜 List My Articles             | List your own published articles                  |
| 📝 List My Draft Articles       | List your own draft articles                      |
| 📝 List My Unpublished Articles | List your own unpublished articles                |
| 📝 List My Scheduled Articles   | List your own scheduled articles                  |
| 🧑‍💻 Publish Article by ID        | Publish your own articles by ID                  |
| 📝 Publish Article by Title     | Publish your own articles by title               |
| 🧑‍💻 Unpublish Article by ID      | Unpublish your own articles by ID                |
| 📝 Unpublish Article by Title   | Unpublish your own articles by title             |
| 📝 Delete Article               | Delete your own articles                          |

---

## 🧠 Analyze Tools

| Feature                  | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| 🧠 Analyze Article        | Analyze a specific article (prompt-based, summary output)    |
| 🧠 Analyze User Profile   | Analyze a specific user profile (prompt-based, summary output)|

> **Note:** Analyze tools provide natural language summaries and insights, not raw data dumps.

---

## 📝 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.

**COMMERCIAL USE WARNING** 

If you want to use or deploy this code in any form as a monetised service to others, even if you don't specifically require payment for the code, you need to contact me for permission (this means _YOU_ Smithery/Glama or ANY similar services) - which will only be granted following payment of the appropriate licensing fee. No, you might not be charging for the use of the code itself, and you might be providing the infrastructure, but you'd be using _MY_ code to facilitate _YOUR_ service. That's an intrinsic dependency that **MUST** be licensed. 

For anyone else, whether you're a business or individual, I hope it's of use to you. Enjoy.

---

## ⚙️ Server Configuration

The server can be configured using the following environment variables:

| Environment Variable | Description                   | Default |
|---------------------|-------------------------------|---------|
| `PORT`              | Port to run the server on      | `8000`  |
| `LOG_LEVEL`         | Logging level (INFO, DEBUG, etc.) | `INFO`  |

---

## 🔐 Client Authentication

Each client needs to provide their own Dev.to API key for authenticated operations. This is done securely by providing the API key as an environment variable in the client's MCP server configuration.

> **Note:** The key should be provided as `DEVTO_API_KEY` in the environment section of your MCP client configuration.

---

## 🚀 Getting Started

### 🐳 Running with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/rawveg/devtomcp.git
cd devtomcp
```

2. **Build and run with Docker Compose:**

```bash
docker-compose up --build
```

The server will be available at [http://localhost:8000](http://localhost:8000) with the SSE endpoint at [http://localhost:8000/sse](http://localhost:8000/sse).

---

## 🛠️ MCP Tools

### Browsing Content
- `browse_latest_articles()` - Get the most recent articles from Dev.to
- `browse_popular_articles()` - Get the most popular articles
- `browse_articles_by_tag(tag)` - Get articles with a specific tag

### Reading Content
- `get_article(id)` - Get detailed information about a specific article
- `get_user_profile(username)` - Get information about a Dev.to user

### Searching Content
- `search_articles(query, page=1)` - Search for articles using keywords
- `search_articles_by_user(username, page=1)` - Search all articles by a specific user

### Managing Content (requires authentication)
- `list_my_articles(page=1, per_page=30)` - List your own published articles
- `list_my_draft_articles(page=1, per_page=30)` - List your own draft articles
- `list_my_unpublished_articles(page=1, per_page=30)` - List your own unpublished articles
- `create_article(title, content, tags="", published=False)` - Create a new article
- `update_article(id, title=None, content=None, tags=None, published=None)` - Update an existing article
- `delete_article(id)` - Delete an existing article
- `publish_article_by_id(id)` - Publish your own articles by ID
- `publish_article_by_title(title)` - Publish your own articles by title
- `unpublish_article_by_id(id)` - Unpublish your own articles by ID
- `unpublish_article_by_title(title)` - Unpublish your own articles by title

---

## 🖥️ Client Configuration

### Claude Desktop Configuration

Add the MCP server in Claude Desktop's `config.json`:

```json
{
  "mcpServers": {
    "devto": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Cursor Configuration

Add the MCP server in Cursor's configuration:

```json
{
  "mcpServers": {
    "devto": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**NOTE** 

Some clients may require the use of `serverUrl` instead of `url`, eg: Windsurf IDE by Codium.

### Programmatic Access with Python

```python
import asyncio
import os
from fastmcp.client import Client

async def main():
    # Set environment variable for authentication
    os.environ["DEVTO_API_KEY"] = "your_dev_to_api_key_here"
    
    # Connect to the MCP server
    client = Client("http://localhost:8000/sse")
    
    # Use the client
    async with client:
        # Get popular articles
        results = await client.call_tool("browse_popular_articles", {})
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ☁️ Deploying to Google Cloud Run

For deploying to Google Cloud Run:

1. Follow the [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy) to set up your environment
2. Set up your Dev.to API key as a secret:
   ```bash
   gcloud secrets create devto-api-key --data-file=- <<< "your_api_key_here"
   ```
3. Deploy with the secret mounted:
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

   **Environment Variables**
   
   | Variable | Description | Default |
   | --- | --- | --- |
   | `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | `INFO` |
   | `DEVTO_API_KEY` | Dev.to API key | `None` |
   | `DEVTO_API_BASE_URL` | Dev.to API base URL | `https://dev.to/api` |

   These variables must be set on the command line for gcloud run deploy as the .env file is not mounted to the container.

  **Region Selection**
  The region should be selected according to the region of your associated project. A list of available regions can be found [here](https://cloud.google.com/run/docs/locations).

⚠️ **Security Warning:** 
- The `--allow-unauthenticated` flag makes your server publicly accessible
- Since this is a single-user server with your API key, you MUST implement additional security measures:
  - Use [Cloud Run Authentication](https://cloud.google.com/run/docs/authenticating/overview)
  - Set up [Identity-Aware Proxy (IAP)](https://cloud.google.com/iap/docs/cloud-run-tutorial)
  - Configure [VPC Service Controls](https://cloud.google.com/vpc-service-controls/docs/overview)
  - Use [Ingress Controls](https://cloud.google.com/run/docs/securing/ingress)

See [GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md) for detailed security configuration instructions.

---

## ⚠️ Error Handling

The server returns standard MCP error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "code": 401
}
```

Common error codes:
- **401**: Authentication failed (missing or invalid API key)
- **404**: Resource not found
- **422**: Invalid parameters
- **500**: Server error

---

## 🔒 Security Considerations

- The server uses environment variables for API key configuration, providing proper security isolation
- Each client connection uses its own configured API key
- All API credential handling happens server-side
- Use HTTPS in production environments
- Use secure secret management for API keys in cloud deployments

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 🙏 Acknowledgments

- [Dev.to API Documentation](https://developers.forem.com/api)
- [Model Context Protocol](https://modelcontextprotocol.github.io/)

---

## 📬 Contact

For questions, suggestions, or support, please open an issue or contact the maintainer at [your.email@example.com](mailto:your.email@example.com). 