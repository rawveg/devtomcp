"""
Prompt generation functions for Dev.to article-related operations.
"""
from typing import Optional

def get_article_prompt(article_id: str) -> str:
    """Create a prompt to get a specific article"""
    return f"Please get the Dev.to article with ID {article_id} and provide a summary of its key points and insights."

def get_article_by_title_prompt(article_title: str) -> str:
    """Create a prompt to get a specific article by title"""
    return f"Please get the Dev.to article with title '{article_title}' and provide a summary of its key points and insights."

def list_my_articles_prompt(page: Optional[int] = 1, per_page: Optional[int] = 30) -> str:
    """Create a prompt to list my published articles"""
    if page == 1 and per_page == 30:
        return "Please list my published articles on Dev.to."
    elif page == 1:
        return f"Please list my published articles on Dev.to, showing {per_page} articles per page."
    elif per_page == 30:
        return f"Please list my published articles on Dev.to, starting from page {page}."
    else:
        return f"Please list my published articles on Dev.to, showing {per_page} articles per page starting from page {page}."

def create_article_prompt(title: str, content: str, tags: Optional[str] = "", published: Optional[bool] = False) -> str:
    """Create a prompt to create a new article"""
    prompt = f"Please create a new article on Dev.to with title '{title}' and content: {content}"
    if tags:
        prompt += f", tagged with: {tags}"
    if published:
        prompt += " and publish it immediately"
    else:
        prompt += " as a draft"
    return prompt + "."

def update_article_prompt(id: str, title: Optional[str] = None, content: Optional[str] = None, 
                        tags: Optional[str] = None, published: Optional[bool] = None) -> str:
    """Create a prompt to update an existing article"""
    prompt = f"Please update the article with ID {id} on Dev.to with the following changes:"
    changes = []
    if title is not None:
        changes.append(f"new title: '{title}'")
    if content is not None:
        changes.append(f"new content: {content}")
    if tags is not None:
        changes.append(f"new tags: {tags}")
    if published is not None:
        changes.append("publish it" if published else "save as draft")
    return prompt + " " + ", ".join(changes) + "."

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

def list_my_draft_articles_prompt(page: Optional[int] = 1, per_page: Optional[int] = 30) -> str:
    """Create a prompt to list draft articles"""
    if page == 1 and per_page == 30:
        return "Please list my draft articles on Dev.to."
    elif page == 1:
        return f"Please list my draft articles on Dev.to, showing {per_page} articles per page."
    elif per_page == 30:
        return f"Please list my draft articles on Dev.to, starting from page {page}."
    else:
        return f"Please list my draft articles on Dev.to, showing {per_page} articles per page starting from page {page}."

def list_my_unpublished_articles_prompt(page: Optional[int] = 1, per_page: Optional[int] = 30) -> str:
    """Create a prompt to list unpublished articles"""
    if page == 1 and per_page == 30:
        return "Please list my unpublished articles on Dev.to."
    elif page == 1:
        return f"Please list my unpublished articles on Dev.to, showing {per_page} articles per page."
    elif per_page == 30:
        return f"Please list my unpublished articles on Dev.to, starting from page {page}."
    else:
        return f"Please list my unpublished articles on Dev.to, showing {per_page} articles per page starting from page {page}."

def list_my_scheduled_articles_prompt(page: Optional[int] = 1, per_page: Optional[int] = 30) -> str:
    """Create a prompt to list scheduled articles"""
    if page == 1 and per_page == 30:
        return "Please list my scheduled articles on Dev.to."
    elif page == 1:
        return f"Please list my scheduled articles on Dev.to, showing {per_page} articles per page."
    elif per_page == 30:
        return f"Please list my scheduled articles on Dev.to, starting from page {page}."
    else:
        return f"Please list my scheduled articles on Dev.to, showing {per_page} articles per page starting from page {page}."

def publish_article_prompt(article_id: str) -> str:
    """Create a prompt to publish an article"""
    return f"Please publish the article with ID {article_id} on Dev.to."

def publish_article_by_title_prompt(title: str) -> str:
    """Create a prompt to publish an article by title"""
    return f"Please publish the article with title '{title}' on Dev.to."

def unpublish_article_prompt(article_id: str) -> str:
    """Create a prompt to unpublish an article"""
    return f"Please unpublish the article with ID {article_id} on Dev.to."

def unpublish_article_by_title_prompt(title: str) -> str:
    """Create a prompt to unpublish an article by title"""
    return f"Please unpublish the article with title '{title}' on Dev.to."

def update_article_by_title_prompt(title: str, new_title: Optional[str] = None, content: Optional[str] = None, tags: Optional[str] = None, published: Optional[bool] = None) -> str:
    """Create a prompt to update an article by title"""
    prompt = f"Please update the article with title '{title}' on Dev.to"
    changes = []
    if new_title is not None:
        changes.append(f"new title: '{new_title}'")
    if content is not None:
        changes.append(f"new content: {content}")
    if tags is not None:
        changes.append(f"new tags: {tags}")
    if published is not None:
        changes.append("publish it" if published else "save as draft")
    if changes:
        prompt += " with the following changes: " + ", ".join(changes)
    prompt += "."
    return prompt
    
