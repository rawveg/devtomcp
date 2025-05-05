"""
Prompt generation functions for Dev.to user-related operations.
"""

def get_user_profile_prompt(username: str) -> str:
    """Create a prompt to get a specific user profile"""
    return f"Please get the Dev.to user profile with username {username} and provide a summary of its key points and insights."

def analyze_user_profile(username: str) -> str:
    """Create a prompt to analyze a specific user profile"""
    return f"Please analyze the Dev.to user profile with username {username} and provide a summary of its key points and insights."

def analyze_user_profile_by_id(user_id: str) -> str:
    """Create a prompt to analyze a specific user profile by ID"""
    return f"Please analyze the Dev.to user profile with ID {user_id} and provide a summary of its key points and insights."
