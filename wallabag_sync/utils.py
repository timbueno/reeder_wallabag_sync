import hashlib
import os
import requests
from typing import Dict, List, Any, Union
from requests.exceptions import RequestException
from dotenv import load_dotenv

def hash_url(url: Union[str, bytes]) -> str:
    """Hash a URL using SHA1.
    
    Args:
        url: The URL to hash, either as a string or bytes
        
    Returns:
        A 40-character hexadecimal string containing the SHA1 hash
        
    Raises:
        TypeError: If the URL is not a string or bytes
    """
    if isinstance(url, str):
        url_bytes = url.encode('utf-8')
    elif isinstance(url, bytes):
        url_bytes = url
    else:
        raise TypeError("URL must be a string or bytes")
    
    return hashlib.sha1(url_bytes).hexdigest()

def load_config(load_env_file: bool = True) -> dict:
    """Load configuration from environment variables.
    
    Args:
        load_env_file: Whether to load variables from .env file
        
    Returns:
        A dictionary containing the configuration values
        
    Raises:
        KeyError: If a required environment variable is missing
    """
    # Required environment variables
    required_vars = [
        'FEED_URL',
        'WALLABAG_BASE_URL',
        'WALLABAG_CLIENT_ID',
        'WALLABAG_CLIENT_SECRET',
        'WALLABAG_USERNAME',
        'WALLABAG_PASSWORD'
    ]
    
    # Load .env file if requested
    if load_env_file:
        load_dotenv()
    
    # Check for required variables
    config = {}
    for var in required_vars:
        if var not in os.environ:
            raise KeyError(f"Missing required environment variable: {var}")
        config[var] = os.environ[var]
    
    return config

def fetch_feed(feed_url: str) -> Dict[str, Any]:
    """
    Fetch and parse the JSON feed.
    
    Args:
        feed_url (str): URL of the JSON feed
        
    Returns:
        Dict[str, Any]: Parsed JSON feed data
        
    Raises:
        RequestException: If there's an error fetching the feed
        ValueError: If the feed is not valid JSON
    """
    try:
        response = requests.get(feed_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while fetching feed")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error fetching feed: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid JSON feed: {str(e)}")

def extract_urls(feed_json: Dict[str, Any]) -> List[str]:
    """
    Extract article URLs from the feed JSON.
    
    Args:
        feed_json (Dict[str, Any]): Parsed JSON feed data
        
    Returns:
        List[str]: List of article URLs
        
    Raises:
        ValueError: If the feed has an invalid structure
    """
    if not isinstance(feed_json, dict):
        raise ValueError("Feed must be a JSON object")
        
    items = feed_json.get('items', [])
    if not isinstance(items, list):
        raise ValueError("Feed must contain an 'items' array")
        
    urls = []
    for item in items:
        if not isinstance(item, dict):
            continue
            
        url = item.get('url')
        if isinstance(url, str):
            urls.append(url)
            
    return urls 