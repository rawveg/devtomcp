#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dev.to MCP Server - A server implementation for interacting with Dev.to API

This program provides an MCP server interface to the Dev.to API.

Copyright (C) 2023 <Your Name/Organization>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union, Annotated, Iterator
from dotenv import load_dotenv
from datetime import datetime
import threading
import re

# Load environment variables from .env file
load_dotenv()

import httpx
from fastapi import FastAPI, Request, Response, Query, Body, Path, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Load configuration from environment variables
PORT = int(os.environ.get("PORT", 8080))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
REST_PORT = int(os.environ.get("REST_PORT", 8001))

# Configure logging based on environment variable
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("devto-mcp")

# Log configuration (without sensitive data)
logger.info(f"Starting server with PORT={PORT}, LOG_LEVEL={LOG_LEVEL}, REST_PORT={REST_PORT}")

# Constants
DEVTO_API_BASE_URL = "https://dev.to/api"

# API client for Dev.to interactions
class DevToClient:
    """Client for interacting with the Dev.to API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the Dev.to API client."""
        self.base_url = DEVTO_API_BASE_URL
        self.api_key = api_key
        
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request to the Dev.to API."""
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            url = f"{self.base_url}{path}"
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    
    async def post(self, path: str, data: Dict[str, Any]) -> Any:
        """Make a POST request to the Dev.to API."""
        if not self.api_key:
            raise ValueError("Dev.to API key is required for POST operations")
            
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            url = f"{self.base_url}{path}"
            response = await client.post(url, json=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    async def put(self, path: str, data: Dict[str, Any]) -> Any:
        """Make a PUT request to the Dev.to API."""
        if not self.api_key:
            raise ValueError("Dev.to API key is required for PUT operations")
            
        async with httpx.AsyncClient() as client:
            headers = await self._get_headers()
            url = f"{self.base_url}{path}"
            response = await client.put(url, json=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()

# Custom exception for MCP-related errors
class MCPError(Exception):
    """Custom exception for MCP-related errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Create FastAPI app for health checks and info endpoints
app = FastAPI(
    title="Dev.to MCP Server",
    description="An MCP server for interacting with the Dev.to API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server
mcp = FastMCP(
    name="Dev.to API",
    description="MCP server for interacting with the Dev.to API",
    instructions="""
    # Dev.to API MCP Server
    
    This server provides tools for interacting with the Dev.to API, 
    allowing you to browse, search, read, and create content.
    
    ## Required Configuration
    
    This MCP server requires a Dev.to API key to function properly.
    Please provide your Dev.to API key in the server environment:
    
    ```bash
    export DEVTO_API_KEY="your_dev_to_api_key_here"
    ```
    
    ## Available Tools
    
    ### Browsing Content
    - browse_latest_articles(): Get recent articles from Dev.to
    - browse_popular_articles(): Get popular articles
    - browse_articles_by_tag(tag): Get articles with a specific tag
    - browse_articles_by_title(title): Get articles with a specific title
    
    ### Reading Content  
    - get_article(id): Get article details by ID
    - get_article_by_title(title): Get article details by title
    - get_user_profile(username): Get information about a Dev.to user
    - get_article_by_id(id): Get article details by ID
    - analyze_article(id): Analyze a specific article
    - analyze_user_profile(username): Analyze a specific user profile

    
    ### Searching Content
    - search_articles(query, page): Search for articles by keywords
    
    ### Managing Content
    - list_my_articles(page, per_page): List your published articles
    - list_my_draft_articles(page, per_page): List your draft articles
    - list_my_unpublished_articles(page, per_page): List your unpublished articles
    - list_my_scheduled_articles(page, per_page): List your scheduled articles
    - create_article(title, content, tags, published): Create a new article
    - update_article(id, title, content, tags, published): Update an existing article
    - delete_article(id): Delete an existing article
    - publish_article(id): Publish an existing article
    - publish_article_by_title(title): Publish an existing article by title
    - unpublish_article(id): Unpublish an existing article
    - unpublish_article_by_title(title): Unpublish an existing article by title
    
    ## Examples
    - To find Python articles: search_articles("python")
    - To get an article: get_article(12345)
    - To get an article by title: get_article_by_title("Title")
    - To create an article: create_article("Title", "Content", "tag1,tag2", false)
    - To update an article: update_article(12345, "Title", "Content", "tag1,tag2", false)
    - To see your articles: list_my_articles()
    - To see your draft articles: list_my_draft_articles()
    - To see your unpublished articles: list_my_unpublished_articles()
    - To see your scheduled articles: list_my_scheduled_articles()
    - To delete an article: delete_article(12345)
    - To publish an article: publish_article(12345)
    - To publish an article by title: publish_article_by_title("Title")
    - To unpublish an article: unpublish_article(12345)
    - To unpublish an article by title: unpublish_article_by_title("Title")
    - To get user profile: get_user_profile("username")
    - To search articles: search_articles("query")
    """
)

# Import prompts from the new modules
from prompts.article_prompts import (
    get_article_prompt,
    get_article_by_title_prompt,
    list_my_articles_prompt,
    list_my_draft_articles_prompt,
    list_my_unpublished_articles_prompt,
    list_my_scheduled_articles_prompt,
    create_article_prompt,
    update_article_prompt,
    delete_article_prompt,
    get_article_by_id_prompt,
    search_articles_prompt,
    publish_article_prompt,
    publish_article_by_title_prompt,
    unpublish_article_prompt,
    unpublish_article_by_title_prompt,
    analyze_article
)
from prompts.user_prompts import (
    get_user_profile_prompt,
    analyze_user_profile,
    analyze_user_profile_by_id
)

# Register prompts with MCP server
get_article_prompt = mcp.prompt()(get_article_prompt)
get_article_by_title_prompt = mcp.prompt()(get_article_by_title_prompt)
list_my_articles_prompt = mcp.prompt()(list_my_articles_prompt)
list_my_draft_articles_prompt = mcp.prompt()(list_my_draft_articles_prompt)
list_my_unpublished_articles_prompt = mcp.prompt()(list_my_unpublished_articles_prompt)
list_my_scheduled_articles_prompt = mcp.prompt()(list_my_scheduled_articles_prompt)
create_article_prompt = mcp.prompt()(create_article_prompt)
update_article_prompt = mcp.prompt()(update_article_prompt)
delete_article_prompt = mcp.prompt()(delete_article_prompt)
get_article_by_id_prompt = mcp.prompt()(get_article_by_id_prompt)
search_articles_prompt = mcp.prompt()(search_articles_prompt)
analyze_article = mcp.prompt()(analyze_article)
get_user_profile_prompt = mcp.prompt()(get_user_profile_prompt)
analyze_user_profile = mcp.prompt()(analyze_user_profile)
analyze_user_profile_by_id = mcp.prompt()(analyze_user_profile_by_id)
publish_article_prompt = mcp.prompt()(publish_article_prompt)
publish_article_by_title_prompt = mcp.prompt()(publish_article_by_title_prompt)
unpublish_article_prompt = mcp.prompt()(unpublish_article_prompt)
unpublish_article_by_title_prompt = mcp.prompt()(unpublish_article_by_title_prompt)

# Helper functions for formatting responses
def format_article_list(articles: List[Dict[str, Any]]) -> str:
    """Format a list of articles for display."""
    if not articles:
        return "No articles found."
        
    result = []
    result.append("# Articles")
    result.append("")
    
    for article in articles:
        title = article.get("title", "Untitled")
        id = article.get("id", "Unknown ID")
        username = article.get("user", {}).get("username", "unknown")
        date = article.get("published_at", "Unknown date")
        tags = article.get("tag_list", [])
        tags_str = ", ".join(tags) if isinstance(tags, list) else tags
        
        result.append(f"## {title}")
        result.append(f"ID: {id}")
        result.append(f"Author: {username}")
        result.append(f"Published: {date}")
        result.append(f"Tags: {tags_str}")
        result.append(f"URL: {article.get('url', '')}")
        result.append("")
        result.append(article.get("description", "No description available."))
        result.append("")
    
    return "\n".join(result)

def ensure_list(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [t.strip() for t in val.split(",") if t.strip()]
    return []

def format_article_detail(article: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": article.get("id"),
        "title": article.get("title", "Untitled"),
        "url": article.get("url", ""),
        "published_at": article.get("published_at"),
        "description": article.get("description"),
        "tags": ensure_list(article.get("tag_list", article.get("tags", []))),
        "author": article.get("user", {}).get("username", "unknown"),
        "published": bool(article.get("published", False)),
        "body_markdown": article.get("body_markdown"),
        "body_html": article.get("body_html"),
        "content": article.get("body_markdown") or article.get("body_html") or "",
    }

async def find_all_my_articles(api_key: str = None) -> List[Dict[str, Any]]:
    """
    Retrieve all articles (published, drafts, scheduled) belonging to the authenticated user.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        client = DevToClient(api_key=api_key)
        articles = await client.get("/articles/me/all")
        return articles
    except Exception as e:
        logger.error(f"Error finding all my articles: {str(e)}")
        raise MCPError(f"Failed to find all my articles: {str(e)}")

def format_article_list(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format a list of articles."""
    if not articles:
        return []
        
    return [{
        "id": article.get("id", "Unknown ID"),
        "title": article.get("title", "Untitled"),
        "url": article.get("url", ""),
        "published_at": article.get("published_at", "Unknown date"),
        "description": article.get("description", ""),
        "tags": article.get("tag_list", []),
        "author": article.get("user", {}).get("username", "unknown")
    } for article in articles]

def format_user_profile(user: Dict[str, Any]) -> Dict[str, Any]:
    """Format user profile information."""
    if not user:
        return {"error": "User not found."}
        
    return {
        "name": user.get("name", "Unknown"),
        "username": user.get("username", "unknown"),
        "bio": user.get("summary", "No bio available."),
        "location": user.get("location", ""),
        "joined_at": user.get("joined_at", ""),
        "twitter_username": user.get("twitter_username", ""),
        "github_username": user.get("github_username", ""),
        "website_url": user.get("website_url", "")
    }

# Helper function to get API key from server environment
def get_api_key(request: Request = None) -> str:
    """Get the API key from server environment."""
    mode = os.environ.get("SERVER_MODE", "sse").lower()
    if mode == "rest":
        if request is None:
            return None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        return None
    else:
        return os.environ.get('DEVTO_API_KEY')

# Helper class for returning structured data directly (without using MCPResponse)
class ArticleListResponse:
    """Helper to format article data as structured content."""
    
    @staticmethod
    def create(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a properly structured response with the articles as direct content."""
        # Return the articles directly as a list - FastMCP will handle the proper serialization
        return articles
        
# Function to convert raw articles to a simplified list with essential details
def simplify_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert raw article data to a simplified list with essential details."""
    def get_published(article):
        # If 'published' is missing, treat as False (unpublished)
        if "published" not in article:
            return False
        # If present but None, treat as False
        return bool(article.get("published", False))
    return [
        {
            "id": article.get("id"),
            "title": article.get("title"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "description": article.get("description"),
            "tags": ensure_list(article.get("tag_list", article.get("tags", []))),
            "author": article.get("user", {}).get("username") if article.get("user") else None,
            "published": get_published(article)
        }
        for article in articles
    ]

# Pydantic models
class ArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: Optional[str]
    description: str
    tags: List[str]
    author: str
    published: bool

class ScheduledArticleResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: Optional[str]
    description: str
    tags: List[str]
    author: str
    scheduled: bool = Field(..., description="True if the article is scheduled for future publication.")
    published: bool

class ArticleDetailResponse(BaseModel):
    id: int
    title: str
    url: str
    published_at: Optional[str]
    description: Optional[str]
    tags: List[str]
    author: str
    published: bool
    body_markdown: Optional[str]
    body_html: Optional[str]
    content: Optional[str]

# MCP Tool implementations

@mcp.tool()
async def browse_latest_articles(
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    per_page: Annotated[int, Field(description="Number of articles per page")] = 30,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 10,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Get the most recent articles from Dev.to across multiple pages.
    
    This tool will fetch recent articles from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Track all articles across multiple pages
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we reach the limit or run out of results
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get("/articles/latest", params={
                    "page": current_page,
                    "per_page": per_page
                })
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Add articles to our collection
                all_articles.extend(articles)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error fetching latest articles page {current_page}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error getting latest articles: {str(e)}")
        raise MCPError(f"Failed to get latest articles: {str(e)}")

@mcp.tool()
async def browse_popular_articles(
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    per_page: Annotated[int, Field(description="Number of articles per page")] = 30,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 10,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Get the most popular articles from Dev.to across multiple pages.
    
    This tool will fetch popular articles from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Track all articles across multiple pages
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we reach the limit or run out of results
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get("/articles", params={
                    "page": current_page,
                    "per_page": per_page
                })
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Add articles to our collection
                all_articles.extend(articles)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error fetching popular articles page {current_page}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error getting popular articles: {str(e)}")
        raise MCPError(f"Failed to get popular articles: {str(e)}")

@mcp.tool()
async def browse_articles_by_tag(
    tag: Annotated[str, Field(description="The tag to filter articles by")],
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    per_page: Annotated[int, Field(description="Number of articles per page")] = 30,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 10,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Get articles with a specific tag across multiple pages.
    
    This tool will fetch articles with the specified tag from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Track all articles across multiple pages
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we reach the limit or run out of results
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get("/articles", params={
                    "tag": tag,
                    "page": current_page,
                    "per_page": per_page
                })
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Add articles to our collection
                all_articles.extend(articles)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error fetching articles with tag '{tag}' on page {current_page}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error getting articles by tag: {str(e)}")
        raise MCPError(f"Failed to get articles with tag '{tag}': {str(e)}")

@mcp.tool()
async def get_article(
    id: Annotated[str, Field(description="The ID of the article to retrieve")],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get a specific article by ID.
    """
    try:
        client = DevToClient(api_key=get_api_key())
        # 1. Try public endpoint first
        try:
            article = await client.get(f"/articles/{id}")
            return format_article_detail(article)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        # 2. Fallback: search /articles/me/all for unpublished articles only
        page = 1
        per_page = 30
        max_pages = 10
        while page <= max_pages:
            articles = await client.get("/articles/me/all", params={"page": page, "per_page": per_page})
            for article in articles:
                if article.get("published"):
                    # Stop searching—published articles are accessible via public endpoint
                    return {"error": f"Article not found with ID: {id}"}
                if str(article.get("id")) == str(id):
                    return format_article_detail(article)
            if not articles or len(articles) == 0:
                break
            page += 1
        return {"error": f"Article not found with ID: {id}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_article_by_title(
    title: Annotated[str, Field(description="The title of the article")],
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Get a specific article by title.

    This tool will search for articles on Dev.to, looking through multiple
    pages until it finds matches or reaches the maximum page limit. If not found
    it will fallback to the User's articles and filter based on title to retrieve the id
    """
    try:
        client = DevToClient(api_key=get_api_key() if api_key is None else api_key)
        try:
            articles = await search_articles(title)
            article = next((article for article in articles if article["title"] == title), None)
            if article is None:
                articles = await find_all_my_articles(api_key=api_key)
                article = next((article for article in articles if article.get("title", "").lower() == title.lower()), None)
                if article is None:
                    raise MCPError(f"Article not found with title: {title}", 404)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MCPError(f"Article not found with fallback title: {title}", 404)
            else:
                raise
        return format_article_detail(article)
    except Exception as e:
        logger.error(f"Error getting article {title}: {str(e)}")
        raise MCPError(f"Failed to get article {title}: {str(e)}")

@mcp.tool()
async def get_user_profile(
    username: Annotated[str, Field(description="The username of the Dev.to user")],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get profile information for a Dev.to user.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        user = await client.get(f"/users/by_username?url={username}")
        return format_user_profile(user)
    except Exception as e:
        logger.error(f"Error getting user profile for {username}: {str(e)}")
        raise MCPError(f"Failed to get profile for user '{username}': {str(e)}")

@mcp.tool()
async def search_articles(
    query: Annotated[str, Field(description="The search term")],
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 30,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Search for articles on Dev.to across multiple pages.
    
    This tool will search through articles on Dev.to, looking through multiple
    pages until it finds matches or reaches the maximum page limit.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Track all matching articles
        all_matching_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we find matches or reach the limit
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get("/articles", params={"page": current_page})
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Filter articles containing the query in title or description
                page_matches = [
                    article for article in articles
                    if (query.lower() in article.get("title", "").lower() or
                        query.lower() in article.get("description", "").lower() or
                        (isinstance(article.get("tag_list"), list) and 
                         any(query.lower() in tag.lower() for tag in article.get("tag_list", []))) or
                        (isinstance(article.get("user"), dict) and
                         query.lower() in article.get("user", {}).get("username", "").lower()) or
                        query.lower() in article.get("body_markdown", "").lower())
                ]
                
                # Add matching articles to our collection
                all_matching_articles.extend(page_matches)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # If we've found some matches, we can stop searching
                if all_matching_articles:
                    break
                    
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error searching page {current_page}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # If we didn't find anything through pagination, try direct search approaches
        if not all_matching_articles:
            # Try searching by tag if the query looks like a tag
            try:
                tag_articles = await client.get("/articles", params={"tag": query.lower()})
                all_matching_articles.extend(tag_articles)
            except Exception:
                # Ignore errors in fallback searches
                pass
                
            # If query looks like a username, try that
            if not all_matching_articles and " " not in query:
                try:
                    user_articles = await client.get("/articles", params={"username": query.lower()})
                    all_matching_articles.extend(user_articles)
                except Exception:
                    # Ignore errors in fallback searches
                    pass
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_matching_articles)
        # Add a match_type field to indicate these are search results
        for article in simplified_articles:
            article["match_type"] = "search_result"
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error searching articles for '{query}': {str(e)}")
        raise MCPError(f"Failed to search for '{query}': {str(e)}")

@mcp.tool()
async def search_articles_by_user(
    username: Annotated[str, Field(description="The Dev.to username to search articles for")],
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    per_page: Annotated[int, Field(description="Number of articles per page")] = 30,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 30,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Get all articles published by a specific Dev.to user.
    
    This tool will search through all articles by a user, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Track all articles across multiple pages
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we reach the limit or run out of results
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get("/articles", params={
                    "username": username,
                    "page": current_page,
                    "per_page": per_page
                })
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Add articles to our collection
                all_articles.extend(articles)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error searching page {current_page} for user {username}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error fetching articles for user '{username}': {str(e)}")
        raise MCPError(f"Failed to get articles for user '{username}': {str(e)}")

@mcp.tool()
async def list_my_articles(
    page: int = 1,
    per_page: int = 30,
    max_pages: int = 10,
    ctx: Context = None,
    api_key: str = None
) -> List[Dict[str, Any]]:
    """
    List my published articles across multiple pages.
    
    This tool will fetch my articles from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        
        # Create a client with the API key
        client = DevToClient(api_key=api_key)
        
        # Track all articles across multiple pages
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        
        # Report initial progress
        if ctx:
            await ctx.report_progress(progress=10, total=100)
            
        # Search through pages until we reach the limit or run out of results
        while current_page <= max_page_to_search:
            try:
                # Fetch articles for the current page
                articles = await client.get(
                    "/articles/me",
                    params={"page": current_page, "per_page": per_page}
                )
                
                # If we received no articles, we've reached the end
                if not articles or len(articles) == 0:
                    break
                    
                # Add articles to our collection
                all_articles.extend(articles)
                
                # Update progress periodically
                if ctx:
                    progress = min(90, int(10 + (current_page - page) / max_pages * 80))
                    await ctx.report_progress(progress=progress, total=100)
                
                # Move to the next page
                current_page += 1
                
            except Exception as e:
                logger.warning(f"Error fetching my articles on page {current_page}: {str(e)}")
                # Continue to the next page even if there's an error
                current_page += 1
        
        # Complete progress
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error listing user articles: {str(e)}")
        raise MCPError(f"Failed to list my articles: {str(e)}")

@mcp.tool()
async def list_my_draft_articles(
    page: int = 1,
    per_page: int = 30,
    max_pages: int = 10,
    ctx: Context = None,
    api_key: str = None
) -> List[Dict[str, Any]]:
    """
    List my draft articles on Dev.to, paginated.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        client = DevToClient(api_key=api_key)
        all_articles = []
        current_page = page
        max_page_to_search = page + max_pages - 1
        while current_page <= max_page_to_search:
            try:
                articles = await client.get(
                    "/articles/me/unpublished",
                    params={"page": current_page, "per_page": per_page}
                )
                if not articles or len(articles) == 0:
                    break
                all_articles.extend(articles)
                current_page += 1
            except Exception as e:
                logger.warning(f"Error fetching my draft articles on page {current_page}: {str(e)}")
                current_page += 1
        simplified_articles = simplify_articles(all_articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error listing draft articles: {str(e)}")
        raise MCPError(f"Failed to list my draft articles: {str(e)}")

@mcp.tool()
async def list_my_scheduled_articles(
    page: int = 1,
    per_page: int = 30,
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    List my scheduled articles on Dev.to.
    
    This tool will fetch my scheduled articles from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        
        # Create a client with the API key
        client = DevToClient(api_key=api_key)
        
        # Fetch articles for the current page
        articles = await client.get(
            "/articles/me/all",
            params={"page": page, "per_page": per_page}
        )

        # Filter articles to retrieve all articles that are 'published' = true with a 'published_at' date in the future
        articles = [article for article in articles if article["published"] and article["published_at"] > datetime.now().isoformat()]
        
        # Return a simplified list of articles with essential details
        simplified_articles = simplify_articles(articles)
        return ArticleListResponse.create(simplified_articles)
    except Exception as e:
        logger.error(f"Error listing scheduled articles: {str(e)}")
        raise MCPError(f"Failed to list my scheduled articles: {str(e)}") 

def safe_json_payload(data: dict) -> dict:
    # Recursively ensure all strings are valid for JSON
    def clean(val):
        if isinstance(val, str):
            # Remove problematic control characters except newline, carriage return, tab
            return ''.join(c for c in val if c >= ' ' or c in '\n\r\t')
        if isinstance(val, dict):
            return {k: clean(v) for k, v in val.items()}
        if isinstance(val, list):
            return [clean(v) for v in val]
        return val
    return clean(data)

def sanitize_tag(tag: str) -> str:
    # Only allow lowercase alphanumeric and underscores
    return re.sub(r'[^a-z0-9_]', '', tag.lower())

@mcp.tool()
async def create_article(
    title: Annotated[str, Field(description="The title of the article")],
    content: Annotated[str, Field(description="The markdown content of the article")],
    tags: Annotated[str, Field(description="Comma-separated list of tags (e.g., 'python,webdev')")] = "",
    published: Annotated[bool, Field(description="Whether to publish immediately (default: False)")] = False,
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Create a new article on Dev.to.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            return {"error": "API key is required for this operation. Please provide a Dev.to API key in your server environment.", "status_code": 401}
        client = DevToClient(api_key=api_key)
        tag_list = [sanitize_tag(tag.strip()) for tag in tags.split(",") if sanitize_tag(tag.strip())] if tags else []
        article_data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": bool(published),
                **({"tags": tag_list} if tag_list else {})
            }
        }
        article_data = safe_json_payload(article_data)
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        try:
            response = await client.post("/articles", article_data)
        except httpx.HTTPStatusError as e:
            return {"error": f"Dev.to API error: {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code}
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return format_article_detail(response)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def update_article(
    id: Annotated[Union[str, int], Field(description="The ID of the article to update")],
    title: Annotated[Optional[str], Field(description="New title for the article")] = None,
    content: Annotated[Optional[str], Field(description="New markdown content")] = None,
    tags: Annotated[Optional[str], Field(description="New comma-separated list of tags")] = None,
    published: Annotated[Optional[bool], Field(description="New publish status")] = None,
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Update an existing article on Dev.to.
    """
    try:
        if api_key is None:
            api_key = get_api_key()
        if not api_key:
            return {"error": "API key is required for this operation. Please provide a Dev.to API key in your server environment.", "status_code": 401}
        client = DevToClient(api_key=api_key)
        article_data = {"article": {}}
        if title is not None:
            article_data["article"]["title"] = title
        if content is not None:
            article_data["article"]["body_markdown"] = content
        if tags is not None:
            tag_list = [sanitize_tag(tag.strip()) for tag in tags.split(",") if sanitize_tag(tag.strip())]
            if tag_list:
                article_data["article"]["tags"] = tag_list
        if published is not None:
            article_data["article"]["published"] = bool(published)
        article_data = safe_json_payload(article_data)
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=75, total=100)
        try:
            response = await client.put(f"/articles/{id}", article_data)
        except httpx.HTTPStatusError as e:
            return {"error": f"Dev.to API error: {e.response.status_code} - {e.response.text}", "status_code": e.response.status_code}
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return format_article_detail(response)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def publish_article(
    article_id: Annotated[str, Field(description="The ID of the article to publish")],
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Publish an article on Dev.to.
    """
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=75, total=100)
        response = await update_article(article_id, published=True, ctx=ctx, api_key=api_key)
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def publish_article_by_title(
    title: Annotated[str, Field(description="The title of the article to publish")],
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Publish an article on Dev.to. by title
    """
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=75, total=100)
        article = await get_article_by_title(title, api_key=api_key)
        article_id = article.get("id")
        response = await publish_article(article_id, ctx=ctx, api_key=api_key)
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def unpublish_article(
    article_id: Annotated[str, Field(description="The ID of the article to unpublish")],
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Unpublish an article on Dev.to.
    """
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=75, total=100)
        response = await update_article(article_id, published=False, ctx=ctx, api_key=api_key)
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def unpublish_article_by_title(
    title: Annotated[str, Field(description="The title of the article to unpublish")],
    ctx: Context = None,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Unpublish an article on Dev.to. by title
    """
    try:
        if ctx:
            await ctx.report_progress(progress=25, total=100)
        if ctx:
            await ctx.report_progress(progress=75, total=100)
        article = await get_article_by_title(title, api_key=api_key)
        article_id = article.get("id")
        response = await unpublish_article(article_id, ctx=ctx, api_key=api_key)
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        return response
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_article_by_id(
    article_id: Annotated[str, Field(description="The ID of the article to retrieve (as a string)")],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get a specific article by ID (string version).
    """
    try:
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Try to get the article
        try:
            article = await client.get(f"/articles/{article_id}")
            return format_article_detail(article)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                articles = await find_all_my_articles()
                for article in articles:
                    if article.get("id") == article_id:
                        return format_article_detail(article)
                raise MCPError(f"Article not found with ID: {article_id}", 404)
            else:
                raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {str(e)}")
        raise MCPError(f"Failed to get article {article_id}: {str(e)}")

# --- REST API Endpoints for MCP Tools ---
from pydantic import BaseModel

class CreateArticleRequest(BaseModel):
    title: str = Field(..., example="My First Article", description="The title of the article.")
    content: str = Field(..., example="# Hello World\nThis is my article.", description="The markdown content of the article.")
    tags: str = Field("", example="python,webdev", description="Comma-separated list of tags (e.g., 'python,webdev').")
    published: bool = Field(False, example=False, description="Whether to publish immediately (default: False).")

class UpdateArticleRequest(BaseModel):
    id: Union[str, int] = Field(..., example=123456, description="The ID of the article to update.")
    title: Optional[str] = Field(None, example="Updated Title", description="New title for the article.")
    content: Optional[str] = Field(None, example="# Updated Content", description="New markdown content.")
    tags: Optional[str] = Field(None, example="python,ai", description="New comma-separated list of tags.")
    published: Optional[bool] = Field(None, example=True, description="New publish status.")

# Browse latest articles
@app.get("/browse_latest_articles")
async def rest_browse_latest_articles(
    page: int = Query(1),
    per_page: int = Query(30),
    max_pages: int = Query(10)
):
    """REST endpoint: Get the most recent articles from Dev.to across multiple pages."""
    return await browse_latest_articles(page=page, per_page=per_page, max_pages=max_pages)

# Browse popular articles
@app.get("/browse_popular_articles")
async def rest_browse_popular_articles(
    page: int = Query(1),
    per_page: int = Query(30),
    max_pages: int = Query(10)
):
    """REST endpoint: Get the most popular articles from Dev.to across multiple pages."""
    return await browse_popular_articles(page=page, per_page=per_page, max_pages=max_pages)

# Browse articles by tag
@app.get("/browse_articles_by_tag")
async def rest_browse_articles_by_tag(
    tag: str = Query(...),
    page: int = Query(1),
    per_page: int = Query(30),
    max_pages: int = Query(10)
):
    """REST endpoint: Get articles with a specific tag across multiple pages."""
    return await browse_articles_by_tag(tag=tag, page=page, per_page=per_page, max_pages=max_pages)

# Get article by ID
@app.get("/get_article/{id}", response_model=ArticleDetailResponse)
async def rest_get_article(id: str = Path(...)):
    """REST endpoint: Get a specific article by ID."""
    return await get_article(id=id)

# Get article by title
@app.get("/get_article_by_title/{title}", response_model=ArticleDetailResponse)
async def rest_get_article_by_title(title: str = Path(...)):
    """REST endpoint: Get a specific article by title."""
    return await get_article_by_title(title=title)

# Get user profile
@app.get("/get_user_profile/{username}")
async def rest_get_user_profile(username: str = Path(...)):
    """REST endpoint: Get profile information for a Dev.to user."""
    return await get_user_profile(username=username)

# Search articles
@app.get("/search_articles")
async def rest_search_articles(
    query: str = Query(...),
    page: int = Query(1),
    max_pages: int = Query(30)
):
    """REST endpoint: Search for articles on Dev.to across multiple pages."""
    return await search_articles(query=query, page=page, max_pages=max_pages)

# Search articles by user
@app.get("/search_articles_by_user/{username}")
async def rest_search_articles_by_user(
    username: str = Path(...),
    page: int = Query(1),
    per_page: int = Query(30),
    max_pages: int = Query(30)
):
    """REST endpoint: Get all articles published by a specific Dev.to user."""
    return await search_articles_by_user(username=username, page=page, per_page=per_page, max_pages=max_pages)

# List my articles
@app.get("/list_my_articles", tags=["Articles"], summary="List My Published Articles", description="List my published articles across multiple pages. Requires authentication.", response_model=List[ArticleResponse], status_code=status.HTTP_200_OK)
async def rest_list_my_articles(
    page: int = Query(1, description="Starting page number for pagination", example=1),
    per_page: int = Query(30, description="Number of articles per page", example=30),
    max_pages: int = Query(10, description="Maximum number of pages to search", example=1),
    request: Request = None
):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await list_my_articles(page=page, per_page=per_page, max_pages=max_pages, ctx=None, api_key=api_key)

# List my draft articles
@app.get("/list_my_draft_articles", tags=["Articles"], summary="List My Draft Articles", description="List my draft articles on Dev.to. Requires authentication.", response_model=List[ArticleResponse], status_code=status.HTTP_200_OK)
async def rest_list_my_draft_articles(
    page: int = Query(1, description="Starting page number for pagination", example=1),
    per_page: int = Query(30, description="Number of articles per page", example=30),
    request: Request = None
):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await list_my_draft_articles(page=page, per_page=per_page, ctx=None, api_key=api_key)

# List my scheduled articles
@app.get(
    "/list_my_scheduled_articles",
    tags=["Articles"],
    summary="List My Scheduled Articles",
    description="List my scheduled articles on Dev.to. Requires authentication. An article is considered scheduled if 'published' is true and 'published_at' is a future date.",
    response_model=List[ScheduledArticleResponse],
    status_code=status.HTTP_200_OK
)
async def rest_list_my_scheduled_articles(
    page: int = Query(1, description="Starting page number for pagination", example=1),
    per_page: int = Query(30, description="Number of articles per page", example=30),
    request: Request = None
):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    simplified_articles = await list_my_scheduled_articles(page=page, per_page=per_page, ctx=None, api_key=api_key)
    now = datetime.now().isoformat()
    articles = [
        {
            **article,
            "scheduled": article.get("published", False) and article.get("published_at", "") > now
        }
        for article in simplified_articles
    ]
    return articles

# Create article
@app.post("/create_article", tags=["Articles"], summary="Create My Article", description="Create my new article on Dev.to. Requires authentication.", response_model=dict, status_code=status.HTTP_201_CREATED, response_description="The created article.")
async def rest_create_article(request: Request, body: CreateArticleRequest = Body(..., example={"title": "My First Article", "content": "# Hello World\nThis is my article.", "tags": "python,webdev", "published": False})):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await create_article(
        title=body.title,
        content=body.content,
        tags=body.tags,
        published=body.published,
        ctx=None,
        api_key=api_key
    )

# Update article
@app.post("/update_article", tags=["Articles"], summary="Update My Article", description="Update my existing article on Dev.to. Requires authentication.", response_model=dict, status_code=status.HTTP_200_OK, response_description="The updated article.")
async def rest_update_article(request: Request, body: UpdateArticleRequest = Body(..., example={"id": 123456, "title": "Updated Title", "content": "# Updated Content", "tags": "python,ai", "published": True})):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await update_article(
        id=body.id,
        title=body.title,
        content=body.content,
        tags=body.tags,
        published=body.published,
        ctx=None,
        api_key=api_key
    )

# Publish article
@app.post("/publish_article/{article_id}", tags=["Publishing"], summary="Publish Article", description="Publish an article on Dev.to by article ID. Requires authentication.", response_model=dict, status_code=status.HTTP_200_OK, response_description="The published article.")
async def rest_publish_article(article_id: str = Path(..., description="The ID of the article to publish", example="123456"), request: Request = None):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await publish_article(article_id=article_id, ctx=None, api_key=api_key)

# Publish article by title
@app.post("/publish_article_by_title/{title}", tags=["Publishing"], summary="Publish Article by Title", description="Publish an article on Dev.to by title. Requires authentication.", response_model=dict, status_code=status.HTTP_200_OK, response_description="The published article.")
async def rest_publish_article_by_title(title: str = Path(..., description="The title of the article to publish", example="My First Article"), request: Request = None):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await publish_article_by_title(title=title, ctx=None, api_key=api_key)

# Unpublish article
@app.post("/unpublish_article/{article_id}", tags=["Publishing"], summary="Unpublish Article", description="Unpublish an article on Dev.to by article ID. Requires authentication.", response_model=dict, status_code=status.HTTP_200_OK, response_description="The unpublished article.")
async def rest_unpublish_article(article_id: str = Path(..., description="The ID of the article to unpublish", example="123456"), request: Request = None):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await unpublish_article(article_id=article_id, ctx=None, api_key=api_key)

# Unpublish article by title
@app.post("/unpublish_article_by_title/{title}", tags=["Publishing"], summary="Unpublish Article by Title", description="Unpublish an article on Dev.to by title. Requires authentication.", response_model=dict, status_code=status.HTTP_200_OK, response_description="The unpublished article.")
async def rest_unpublish_article_by_title(title: str = Path(..., description="The title of the article to unpublish", example="My First Article"), request: Request = None):
    api_key = get_api_key(request)
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing or invalid API key. Provide as 'Authorization: Bearer <API_KEY>' header.")
    return await unpublish_article_by_title(title=title, ctx=None, api_key=api_key)

# Get article by ID (string version)
@app.get("/get_article_by_id/{article_id}", response_model=ArticleDetailResponse)
async def rest_get_article_by_id(article_id: str = Path(...)):
    """REST endpoint: Get a specific article by ID (string version)."""
    return await get_article_by_id(article_id=article_id)
# --- END REST API Endpoints ---

# API endpoints

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "Dev.to MCP Server",
        "description": "MCP server for interacting with the Dev.to API",
        "version": "1.0.0",
        "endpoints": {
            "sse": "/sse",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Dev.to MCP Server",
        "version": "1.0.0",
    }

# Main entry point - this is where we create our SSE transport
if __name__ == "__main__":
    mode = os.environ.get("SERVER_MODE", "sse").lower()
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting in {mode.upper()} mode on port {port}")

    if mode == "rest":
        import uvicorn
        uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")
    else:
        mcp.run(transport="sse", host="0.0.0.0", port=port) 