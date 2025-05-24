import json
from typing import Dict, Any, List
import requests
from requests.exceptions import RequestException

def fetch_feed(feed_url: str) -> Dict[str, Any]:
    """
    Fetch and parse the JSON feed from the given URL.
    
    Args:
        feed_url (str): URL of the JSON feed to fetch.
        
    Returns:
        Dict[str, Any]: Parsed JSON feed data.
        
    Raises:
        RequestException: If there's an error fetching the feed.
        ValueError: If the response is not valid JSON.
    """
    try:
        # Fetch the feed with a timeout
        response = requests.get(feed_url, timeout=30)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the JSON response
        feed_data = response.json()
        
        return feed_data
        
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while fetching feed")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error fetching feed: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in feed response: {str(e)}")

def extract_urls(feed_json: Dict[str, Any]) -> List[str]:
    """
    Extract article URLs from the feed JSON data.
    
    Args:
        feed_json (Dict[str, Any]): The parsed JSON feed data.
        
    Returns:
        List[str]: List of article URLs.
        
    Raises:
        ValueError: If the feed data is missing required fields or has invalid structure.
    """
    # Check if items field exists
    if 'items' not in feed_json:
        raise ValueError("Feed data missing 'items' field")
    
    # Check if items is a list
    if not isinstance(feed_json['items'], list):
        raise ValueError("Feed data 'items' field must be a list")
        
    # Extract URLs from items
    urls = []
    for item in feed_json['items']:
        if not isinstance(item, dict):
            continue  # Skip non-dict items
        if 'url' not in item:
            continue  # Skip items without URLs
        urls.append(item['url'])
        
    return urls 