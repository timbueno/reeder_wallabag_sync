from typing import Dict, List, Set, Optional, Tuple
import requests
from requests.exceptions import RequestException

def get_access_token(
    base_url: str,
    client_id: str,
    client_secret: str,
    username: str,
    password: str
) -> str:
    """
    Request an access token from Wallabag using OAuth2 password grant.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
        username (str): Wallabag username
        password (str): Wallabag password
        
    Returns:
        str: Access token
        
    Raises:
        RequestException: If there's an error during the request
        ValueError: If the response doesn't contain an access token
    """
    # Construct the token endpoint URL
    token_url = f"{base_url.rstrip('/')}/oauth/v2/token"
    
    # Prepare the request data
    data = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password
    }
    
    try:
        # Make the request
        response = requests.post(token_url, data=data, timeout=30)
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the response
        token_data = response.json()
        
        # Check if we got an access token
        if 'access_token' not in token_data:
            raise ValueError("No access token in response")
            
        return token_data['access_token']
        
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while requesting access token")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error requesting access token: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Invalid token response: {str(e)}")

def get_unread_entries(base_url: str, access_token: str) -> List[Dict[str, any]]:
    """
    Fetch unread entries from Wallabag.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        access_token (str): Valid access token
        
    Returns:
        List[Dict[str, any]]: List of unread entries, each containing at least 'id', 'url', 'given_url', and 'hashed_given_url'
        
    Raises:
        RequestException: If there's an error during the request
        ValueError: If the response has an invalid structure
    """
    # Construct the entries endpoint URL
    entries_url = f"{base_url.rstrip('/')}/api/entries.json"
    
    # Prepare the request parameters
    params = {
        'detail': 'metadata',  # Include metadata but not full content
        'perPage': 500  # Get a reasonable number of entries
    }
    
    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Make the request
        response = requests.get(
            entries_url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Check if we got the expected structure
        if not isinstance(data, dict) or '_embedded' not in data:
            raise ValueError("Invalid response structure")
            
        entries = data['_embedded'].get('items', [])
        
        # Extract required fields from each entry and filter out archived entries
        return [
            {
                'id': entry['id'],
                'url': entry['url'],
                'given_url': entry.get('given_url', entry['url']),  # Fallback to url if given_url not present
                'hashed_given_url': entry['hashed_given_url']
            }
            for entry in entries
            if 'id' in entry and 'url' in entry and 'hashed_given_url' in entry and not entry.get('is_archived', False)
        ]
        
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while fetching entries")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error fetching entries: {str(e)}")
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid entries response: {str(e)}")

def map_entries_to_urls(entries: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Map Wallabag entries to a dictionary of given URLs to entry IDs.
    If a URL already exists in the map, it will be skipped (first entry wins).
    
    Args:
        entries (List[Dict[str, any]]): List of Wallabag entries, each containing at least 'id' and 'given_url'
        
    Returns:
        Dict[str, int]: Dictionary mapping given URLs to Wallabag entry IDs
        
    Raises:
        ValueError: If an entry is missing required fields
    """
    url_map = {}
    
    for entry in entries:
        # Verify required fields
        if 'id' not in entry or 'given_url' not in entry:
            raise ValueError("Entry missing required fields (id, given_url)")
            
        # Skip if URL already exists in the map
        if entry['given_url'] in url_map:
            continue
            
        # Use the given_url from Wallabag
        url_map[entry['given_url']] = entry['id']
    
    return url_map

def find_urls_to_add(feed_urls: List[str], wallabag_urls: Dict[str, int]) -> List[str]:
    """
    Find URLs from the feed that are not yet in Wallabag.
    
    Args:
        feed_urls (List[str]): List of URLs from the feed
        wallabag_urls (Dict[str, int]): Dictionary mapping given URLs to Wallabag entry IDs
        
    Returns:
        List[str]: List of URLs that need to be added to Wallabag
        
    Raises:
        TypeError: If feed_urls contains non-string items
    """
    urls_to_add: List[str] = []
    
    for url in feed_urls:
        if not isinstance(url, str):
            raise TypeError("Feed URLs must be strings")
            
        # If this URL is not in Wallabag, add it to the list
        if url not in wallabag_urls:
            urls_to_add.append(url)
    
    return urls_to_add

def find_urls_to_archive(feed_urls: Set[str], wallabag_urls: Dict[str, int]) -> List[int]:
    """
    Find Wallabag entries that are no longer in the feed and should be archived.
    
    Args:
        feed_urls (Set[str]): Set of URLs from the feed
        wallabag_urls (Dict[str, int]): Dictionary mapping given URLs to Wallabag entry IDs
        
    Returns:
        List[int]: List of Wallabag entry IDs that should be archived
    """
    # Find entries that are in Wallabag but not in the feed
    entries_to_archive = []
    
    for url, entry_id in wallabag_urls.items():
        if url not in feed_urls:
            entries_to_archive.append(entry_id)
    
    return entries_to_archive

def add_article(base_url: str, access_token: str, url: str) -> bool:
    """
    Add an article to Wallabag.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        access_token (str): Valid access token
        url (str): URL of the article to add
        
    Returns:
        Optional[int]: The ID of the newly created entry if successful, None if the article already exists
        
    Raises:
        RequestException: If there's an error during the request
        ValueError: If the response has an invalid structure
    """
    # Construct the entries endpoint URL
    entries_url = f"{base_url.rstrip('/')}/api/entries.json"
    
    # Prepare the request data
    data = {
        'url': url
    }
    
    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Make the request
        response = requests.post(
            entries_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        # If the article already exists, Wallabag returns 200
        if response.status_code == 200:
            return True
        else:
            return False
        
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while adding article")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error adding article: {str(e)}")
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid response: {str(e)}") 

def add_articles(base_url: str, access_token: str, urls: List[str]) -> Tuple[List[int], List[str]]:
    """
    Add multiple articles to Wallabag.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        access_token (str): Valid access token
        urls (List[str]): List of article URLs to add
        
    Returns:
        Tuple[List[int], List[str]]: A tuple containing:
            - List of successfully added article IDs
            - List of URLs that failed to be added
            
    Raises:
        RequestException: If there's an error during the request
    """
    added_ids = []
    failed_urls = []
    
    for url in urls:
        try:
            entry_id = add_article(base_url, access_token, url)
            if entry_id is not None:
                added_ids.append(entry_id)
        except (RequestException, ValueError) as e:
            # Log the error and continue with the next URL
            failed_urls.append(url)
            continue
    
    return added_ids, failed_urls 

def archive_article(base_url: str, access_token: str, entry_id: int) -> bool:
    """
    Archive an article in Wallabag.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        access_token (str): Valid access token
        entry_id (int): ID of the entry to archive
        
    Returns:
        bool: True if the article was successfully archived, False otherwise
        
    Raises:
        RequestException: If there's an error during the request
    """
    # Construct the entry endpoint URL
    entry_url = f"{base_url.rstrip('/')}/api/entries/{entry_id}.json"
    
    # Prepare the request data
    data = {
        'archive': 1  # Set archive flag to true
    }
    
    # Prepare the request headers
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Make the request
        response = requests.patch(
            entry_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        return True
        
    except requests.exceptions.Timeout:
        raise RequestException("Timeout while archiving article")
    except requests.exceptions.RequestException as e:
        raise RequestException(f"Error archiving article: {str(e)}") 

def archive_articles(base_url: str, access_token: str, entry_ids: List[int]) -> Tuple[List[int], List[int]]:
    """
    Archive multiple articles in Wallabag.
    
    Args:
        base_url (str): Base URL of the Wallabag instance
        access_token (str): Valid access token
        entry_ids (List[int]): List of entry IDs to archive
        
    Returns:
        Tuple[List[int], List[int]]: A tuple containing:
            - List of successfully archived entry IDs
            - List of entry IDs that failed to be archived
            
    Raises:
        RequestException: If there's an error during the request
    """
    archived_ids = []
    failed_ids = []
    
    for entry_id in entry_ids:
        try:
            success = archive_article(base_url, access_token, entry_id)
            if success:
                archived_ids.append(entry_id)
        except RequestException as e:
            # Log the error and continue with the next entry
            failed_ids.append(entry_id)
            continue
    
    return archived_ids, failed_ids 