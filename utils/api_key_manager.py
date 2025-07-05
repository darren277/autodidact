""""""
# Utility module for managing encrypted API keys

from models.user import User
from settings import MASTER_ENCRYPTION_KEY

def get_user_api_key(user_sub):
    """
    Retrieve the decrypted API key for a user
    
    Args:
        user_sub (str): The user's Cognito sub identifier
        
    Returns:
        str: The decrypted API key, or None if not found or invalid
    """
    try:
        user = User.find_by_sub(user_sub)
        if not user:
            return None
        
        return user.get_api_key(MASTER_ENCRYPTION_KEY)
    except Exception as e:
        print(f"Error retrieving API key for user {user_sub}: {e}")
        return None

def has_user_api_key(user_sub):
    """
    Check if a user has an API key stored
    
    Args:
        user_sub (str): The user's Cognito sub identifier
        
    Returns:
        bool: True if user has an API key, False otherwise
    """
    try:
        user = User.find_by_sub(user_sub)
        return user is not None and user.encrypted_api_key is not None
    except Exception as e:
        print(f"Error checking API key for user {user_sub}: {e}")
        return False 