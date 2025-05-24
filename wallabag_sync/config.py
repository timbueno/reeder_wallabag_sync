import os
from typing import Dict
from dotenv import load_dotenv

def load_config(load_env_file: bool = True) -> Dict[str, str]:
    """
    Load configuration from environment variables.
    
    Args:
        load_env_file (bool): Whether to load variables from .env file. Defaults to True.
    
    Returns:
        Dict[str, str]: Dictionary containing configuration values.
        
    Raises:
        ValueError: If any required environment variable is missing.
    """
    # Load environment variables from .env file if requested
    if load_env_file:
        load_dotenv()
    
    # Define required environment variables
    required_vars = [
        'FEED_URL',
        'WALLABAG_BASE_URL',
        'WALLABAG_CLIENT_ID',
        'WALLABAG_CLIENT_SECRET',
        'WALLABAG_USERNAME',
        'WALLABAG_PASSWORD'
    ]
    
    # Create config dictionary
    config = {}
    
    # Check each required variable
    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config 