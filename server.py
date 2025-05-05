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

# Load environment variables from .env file
load_dotenv()

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Load configuration from environment variables
PORT = int(os.environ.get("PORT", 8000))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# Configure logging based on environment variable
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("devto-mcp")

# Log configuration (without sensitive data)
logger.info(f"Starting server with PORT={PORT}, LOG_LEVEL={LOG_LEVEL}")

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
    
    ### Reading Content  
    - get_article(id): Get article details by ID
    - get_user_profile(username): Get information about a Dev.to user
    
    ### Searching Content
    - search_articles(query, page): Search for articles by keywords
    
    ### Managing Content
    - list_my_articles(page, per_page): List your published articles
    - create_article(title, content, tags, published): Create a new article
    - update_article(id, title, content, tags, published): Update an existing article
    
    ## Examples
    - To find Python articles: search_articles("python")
    - To get an article: get_article(12345)
    - To create an article: create_article("Title", "Content", "tag1,tag2", false)
    - To see your articles: list_my_articles()
    """
)

# Import prompts from the new modules
from prompts.article_prompts import (
    get_article_prompt,
    list_my_articles_prompt,
    create_article_prompt,
    update_article_prompt,
    delete_article_prompt,
    get_article_by_id_prompt,
    search_articles_prompt,
    analyze_article
)
from prompts.user_prompts import (
    get_user_profile_prompt,
    analyze_user_profile,
    analyze_user_profile_by_id
)

# Register prompts with MCP server
get_article_prompt = mcp.prompt()(get_article_prompt)
list_my_articles_prompt = mcp.prompt()(list_my_articles_prompt)
create_article_prompt = mcp.prompt()(create_article_prompt)
update_article_prompt = mcp.prompt()(update_article_prompt)
delete_article_prompt = mcp.prompt()(delete_article_prompt)
get_article_by_id_prompt = mcp.prompt()(get_article_by_id_prompt)
search_articles_prompt = mcp.prompt()(search_articles_prompt)
analyze_article = mcp.prompt()(analyze_article)
get_user_profile_prompt = mcp.prompt()(get_user_profile_prompt)
analyze_user_profile = mcp.prompt()(analyze_user_profile)
analyze_user_profile_by_id = mcp.prompt()(analyze_user_profile_by_id)

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

def format_article_detail(article: Dict[str, Any]) -> str:
    """Format a single article with full details."""
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

def format_article_detail(article: Dict[str, Any]) -> str:
    """Format a single article with full details."""
    if not article:
        return "Article not found."
        
    return {
        "title": article.get("title", "Untitled"),
        "id": article.get("id", "Unknown ID"),
        "author": article.get("user", {}).get("username", "unknown"),
        "published_at": article.get("published_at", "Unknown date"),
        "tags": article.get("tag_list", []),
        "url": article.get("url", ""),
        "content": article.get("body_markdown", "No content available."),
        "description": article.get("description", ""),
        "comments_count": article.get("comments_count", 0),
        "public_reactions_count": article.get("public_reactions_count", 0),
        "page_views_count": article.get("page_views_count", 0),
        "published": article.get("published", False),
        "organization": article.get("organization", None)
    }

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
def get_api_key() -> str:
    """Get the API key from server environment."""
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
    return [
        {
            "id": article.get("id"),
            "title": article.get("title"),
            "url": article.get("url"),
            "published_at": article.get("published_at"),
            "description": article.get("description"),
            "tags": article.get("tag_list", []),
            "author": article.get("user", {}).get("username") if article.get("user") else None
        }
        for article in articles
    ]

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
        # Create a client with the API key from server environment
        client = DevToClient(api_key=get_api_key())
        
        # Try to get the article
        try:
            article = await client.get(f"/articles/{id}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MCPError(f"Article not found with ID: {id}", 404)
            else:
                raise
                
        return format_article_detail(article)
    except Exception as e:
        logger.error(f"Error getting article {id}: {str(e)}")
        raise MCPError(f"Failed to get article {id}: {str(e)}")

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
    page: Annotated[int, Field(description="Starting page number for pagination")] = 1,
    per_page: Annotated[int, Field(description="Number of articles per page")] = 30,
    max_pages: Annotated[int, Field(description="Maximum number of pages to search")] = 10,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    List your published articles across multiple pages.
    
    This tool will fetch your articles from Dev.to, looking through multiple
    pages until it reaches the maximum page limit.
    """
    try:
        # Get API key from server environment
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
                logger.warning(f"Error fetching your articles on page {current_page}: {str(e)}")
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
        raise MCPError(f"Failed to list your articles: {str(e)}")

@mcp.tool()
async def create_article(
    title: Annotated[str, Field(description="The title of the article")],
    content: Annotated[str, Field(description="The markdown content of the article")],
    tags: Annotated[str, Field(description="Comma-separated list of tags (e.g., 'python,webdev')")] = "",
    published: Annotated[bool, Field(description="Whether to publish immediately (default: False)")] = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a new article on Dev.to.
    """
    try:
        # Get API key from server environment
        api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        
        # Create a client with the API key
        client = DevToClient(api_key=api_key)
        
        # Process tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        # Prepare article data
        article_data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": published,
                "tags": tag_list
            }
        }
        
        # Report progress at the start
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            
        # Report progress before submission
        if ctx:
            await ctx.report_progress(progress=50, total=100)
            
        response = await client.post("/articles", article_data)
        
        # Report progress after completion
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        
        return {
            "title": response.get("title"),
            "id": response.get("id"),
            "url": response.get("url"),
            "status": "Published" if response.get("published") else "Draft"
        }
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        raise MCPError(f"Failed to create article: {str(e)}")

@mcp.tool()
async def update_article(
    id: Annotated[Union[str, int], Field(description="The ID of the article to update")],
    title: Annotated[Optional[str], Field(description="New title for the article")] = None,
    content: Annotated[Optional[str], Field(description="New markdown content")] = None,
    tags: Annotated[Optional[str], Field(description="New comma-separated list of tags")] = None,
    published: Annotated[Optional[bool], Field(description="New publish status")] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Update an existing article on Dev.to.
    """
    try:
        # Get API key from server environment
        api_key = get_api_key()
        if not api_key:
            raise MCPError("API key is required for this operation. Please provide a Dev.to API key in your server environment.", 401)
        
        # Create a client with the API key
        client = DevToClient(api_key=api_key)
        
        # Prepare update data
        article_data = {"article": {}}
        
        if title is not None:
            article_data["article"]["title"] = title
        
        if content is not None:
            article_data["article"]["body_markdown"] = content
        
        if tags is not None:
            tag_list = [tag.strip() for tag in tags.split(",")]
            article_data["article"]["tags"] = tag_list
        
        if published is not None:
            article_data["article"]["published"] = published
        
        # Report progress at the start
        if ctx:
            await ctx.report_progress(progress=25, total=100)
            
        # Report progress before submission
        if ctx:
            await ctx.report_progress(progress=75, total=100)
            
        response = await client.put(f"/articles/{id}", article_data)
        
        # Report progress after completion
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        
        return {
            "title": response.get("title"),
            "id": response.get("id"),
            "url": response.get("url"),
            "status": "Published" if response.get("published") else "Draft"
        }
    except Exception as e:
        logger.error(f"Error updating article: {str(e)}")
        raise MCPError(f"Failed to update article {id}: {str(e)}")

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
                raise MCPError(f"Article not found with ID: {article_id}", 404)
            else:
                raise
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {str(e)}")
        raise MCPError(f"Failed to get article {article_id}: {str(e)}")

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
    # Log server startup information
    logger.info(f"Server will be available at http://0.0.0.0:{PORT}")
    logger.info(f"SSE endpoint: http://0.0.0.0:{PORT}/sse")
    
    # Using FastMCP's built-in run method with SSE transport
    mcp.run(transport="sse", host="0.0.0.0", port=PORT) 