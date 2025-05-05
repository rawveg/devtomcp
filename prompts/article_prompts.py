"""
Prompt generation functions for Dev.to article-related operations.
"""
from typing import Optional

def get_article_prompt(article_id: str) -> str:
    """Create a prompt to get a specific article"""
    return f"Please get the Dev.to article with ID {article_id} and provide a summary of its key points and insights."

def list_my_articles_prompt(page: int, per_page: int) -> str:
    """Create a prompt to list my published articles"""
    return f"Please list my published articles on Dev.to and provide a summary of its key points and insights."

def create_article_prompt(title: str, content: str, tags: str, published: bool) -> str:
    """Create a prompt to create a new article"""
    return f"Please create a new article on Dev.to with title {title}, content {content}, tags {tags}, and published {published}."

def update_article_prompt(id: str, title: str, content: str, tags: str, published: bool) -> str:
    """Create a prompt to update an existing article"""
    return f"Please update the article with ID {id} on Dev.to with title {title}, content {content}, tags {tags}, and published {published}."

def delete_article_prompt(id: str) -> str:
    """Create a prompt to delete an existing article"""
    return f"Please delete the article with ID {id} on Dev.to."

def get_article_by_id_prompt(article_id: str) -> str:
    """Create a prompt to get a specific article by ID"""
    return f"Please get the Dev.to article with ID {article_id} and provide a summary of its key points and insights."

def search_articles_prompt(query: str) -> str:
    """Create a search prompt for Dev.to articles"""
    return f"Please search for articles on Dev.to about {query} and summarize the key findings."

def analyze_article(article_id: str) -> str:
    """Create a prompt to analyze a specific article"""
    return f"Please analyze the Dev.to article with ID {article_id} and provide a summary of its key points and insights."
