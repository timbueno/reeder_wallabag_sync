import pytest
import requests
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from wallabag_sync.wallabag import (
    get_access_token,
    get_unread_entries,
    map_entries_to_urls,
    find_urls_to_add,
    find_urls_to_archive,
    add_article,
    add_articles,
    archive_article,
    archive_articles
)
from wallabag_sync.utils import hash_url
import os

def test_get_access_token_success():
    """Test successful access token request."""
    # Sample token response
    token_response = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "token_type": "bearer",
        "scope": None,
        "refresh_token": "test_refresh_token"
    }
    
    # Mock the requests.post response
    mock_response = Mock()
    mock_response.json.return_value = token_response
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.post', return_value=mock_response):
        token = get_access_token(
            base_url="https://wallabag.example.com",
            client_id="test_client_id",
            client_secret="test_client_secret",
            username="test_user",
            password="test_password"
        )
        
        # Verify the result
        assert token == "test_access_token"

def test_get_access_token_timeout():
    """Test handling of timeout errors."""
    # Mock requests.post to raise a timeout
    with patch('requests.post', side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            get_access_token(
                base_url="https://wallabag.example.com",
                client_id="test_client_id",
                client_secret="test_client_secret",
                username="test_user",
                password="test_password"
            )
        
        assert "Timeout" in str(exc_info.value)

def test_get_access_token_http_error():
    """Test handling of HTTP errors."""
    # Mock requests.post to raise an HTTP error
    with patch('requests.post', side_effect=requests.exceptions.HTTPError):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            get_access_token(
                base_url="https://wallabag.example.com",
                client_id="test_client_id",
                client_secret="test_client_secret",
                username="test_user",
                password="test_password"
            )
        
        assert "Error requesting access token" in str(exc_info.value)

def test_get_access_token_missing_token():
    """Test handling of response without access token."""
    # Mock response without access token
    mock_response = Mock()
    mock_response.json.return_value = {"error": "invalid_grant"}
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.post', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            get_access_token(
                base_url="https://wallabag.example.com",
                client_id="test_client_id",
                client_secret="test_client_secret",
                username="test_user",
                password="test_password"
            )
        
        assert "No access token in response" in str(exc_info.value)

def test_get_unread_entries_success():
    """Test successful fetching of unread entries."""
    # Sample entries response
    entries_response = {
        "_embedded": {
            "items": [
                {
                    "id": 1,
                    "url": "https://example.com/1",
                    "title": "Article 1",
                    "given_url": "https://example.com/1",
                    "hashed_given_url": "hash1",
                    "is_archived": False
                },
                {
                    "id": 2,
                    "url": "https://example.com/2",
                    "title": "Article 2",
                    "given_url": "https://example.com/2",
                    "hashed_given_url": "hash2",
                    "is_archived": False
                }
            ]
        }
    }
    
    # Mock the requests.get response
    mock_response = Mock()
    mock_response.json.return_value = entries_response
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.get', return_value=mock_response):
        entries = get_unread_entries(
            base_url="https://wallabag.example.com",
            access_token="test_token"
        )
        
        # Verify the result
        assert len(entries) == 2
        assert entries[0]["id"] == 1
        assert entries[0]["url"] == "https://example.com/1"
        assert entries[0]["given_url"] == "https://example.com/1"
        assert entries[0]["hashed_given_url"] == "hash1"
        assert entries[1]["id"] == 2
        assert entries[1]["url"] == "https://example.com/2"
        assert entries[1]["given_url"] == "https://example.com/2"
        assert entries[1]["hashed_given_url"] == "hash2"

def test_get_unread_entries_timeout():
    """Test handling of timeout errors."""
    # Mock requests.get to raise a timeout
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            get_unread_entries(
                base_url="https://wallabag.example.com",
                access_token="test_token"
            )
        
        assert "Timeout" in str(exc_info.value)

def test_get_unread_entries_http_error():
    """Test handling of HTTP errors."""
    # Mock requests.get to raise an HTTP error
    with patch('requests.get', side_effect=requests.exceptions.HTTPError):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            get_unread_entries(
                base_url="https://wallabag.example.com",
                access_token="test_token"
            )
        
        assert "Error fetching entries" in str(exc_info.value)

def test_get_unread_entries_invalid_structure():
    """Test handling of invalid response structure."""
    # Mock response with invalid structure
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}  # Missing _embedded
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            get_unread_entries(
                base_url="https://wallabag.example.com",
                access_token="test_token"
            )
        
        assert "Invalid response structure" in str(exc_info.value)

def test_map_entries_to_urls_success():
    """Test successful mapping of entries to URLs."""
    # Sample entries
    entries = [
        {
            "id": 1,
            "url": "https://example.com/article1",
            "given_url": "https://example.com/article1"
        },
        {
            "id": 2,
            "url": "https://example.com/article2",
            "given_url": "https://example.com/article2"
        }
    ]
    
    # Get the URL map
    url_map = map_entries_to_urls(entries)
    
    # Verify the map structure
    assert len(url_map) == 2
    assert url_map["https://example.com/article1"] == 1
    assert url_map["https://example.com/article2"] == 2

def test_map_entries_to_urls_missing_fields():
    """Test handling of entries with missing fields."""
    entries = [
        {"id": 1, "url": "https://example.com/article1"},  # Missing given_url
        {"id": 2, "url": "https://example.com/article2", "given_url": "https://example.com/article2"}
    ]
    
    with pytest.raises(ValueError, match="Entry missing required fields"):
        map_entries_to_urls(entries)

def test_map_entries_to_urls_empty_list():
    """Test mapping an empty list of entries."""
    url_map = map_entries_to_urls([])
    assert len(url_map) == 0

def test_map_entries_to_urls_duplicate_urls():
    """Test handling of entries with duplicate URLs."""
    entries = [
        {
            "id": 1,
            "url": "https://example.com/article",
            "given_url": "https://example.com/article",
            "hashed_given_url": "hash1"
        },
        {
            "id": 2,
            "url": "https://example.com/article",
            "given_url": "https://example.com/article",
            "hashed_given_url": "hash2"
        }
    ]
    
    url_map = map_entries_to_urls(entries)
    
    # Verify that only one URL is in the map (first one wins)
    assert len(url_map) == 1
    assert url_map["https://example.com/article"] == 1  # First entry's ID should be used

def test_find_urls_to_add_success():
    """Test finding URLs that need to be added."""
    # Sample feed URLs
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://example.com/article3"
    ]
    
    # Sample Wallabag entries (article1 and article2 already exist)
    wallabag_entries = [
        {
            "id": 1,
            "url": "https://example.com/article1",
            "given_url": "https://example.com/article1"
        },
        {
            "id": 2,
            "url": "https://example.com/article2",
            "given_url": "https://example.com/article2"
        }
    ]
    
    # Get the URL map
    wallabag_urls = map_entries_to_urls(wallabag_entries)
    
    # Find URLs to add
    urls_to_add = find_urls_to_add(feed_urls, wallabag_urls)
    
    # Verify only article3 needs to be added
    assert len(urls_to_add) == 1
    assert urls_to_add[0] == "https://example.com/article3"

def test_find_urls_to_add_empty_feed():
    """Test finding URLs to add with an empty feed."""
    urls_to_add = find_urls_to_add([], {})
    assert len(urls_to_add) == 0

def test_find_urls_to_add_empty_wallabag():
    """Test finding URLs to add when Wallabag is empty."""
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    
    urls_to_add = find_urls_to_add(feed_urls, {})
    
    # Verify all URLs need to be added
    assert len(urls_to_add) == 2
    assert set(urls_to_add) == set(feed_urls)

def test_find_urls_to_add_invalid_url():
    """Test handling of invalid URL types."""
    feed_urls = [
        "https://example.com/article1",
        123  # type: ignore
    ]
    
    with pytest.raises(TypeError) as exc_info:
        find_urls_to_add(feed_urls, {})
    
    assert "Feed URLs must be strings" in str(exc_info.value)

def test_find_urls_to_add_duplicate_urls():
    """Test handling of duplicate URLs in feed."""
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article1"  # Duplicate URL
    ]
    
    urls_to_add = find_urls_to_add(feed_urls, {})
    
    # Verify duplicate URLs are handled correctly
    assert len(urls_to_add) == 2
    assert urls_to_add == feed_urls  # Both instances should be included

def test_find_urls_to_archive_success():
    """Test finding URLs that need to be archived."""
    # Sample feed URLs
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    
    # Sample Wallabag entries (article3 should be archived)
    wallabag_entries = [
        {
            "id": 1,
            "url": "https://example.com/article1",
            "given_url": "https://example.com/article1"
        },
        {
            "id": 2,
            "url": "https://example.com/article2",
            "given_url": "https://example.com/article2"
        },
        {
            "id": 3,
            "url": "https://example.com/article3",
            "given_url": "https://example.com/article3"  # Not in feed
        }
    ]
    
    # Get the URL map
    wallabag_urls = map_entries_to_urls(wallabag_entries)
    
    # Find entries to archive
    entries_to_archive = find_urls_to_archive(set(feed_urls), wallabag_urls)
    
    # Verify only article3 needs to be archived
    assert len(entries_to_archive) == 1
    assert entries_to_archive[0] == 3

def test_find_urls_to_archive_empty_feed():
    """Test finding URLs to archive with an empty feed."""
    # Sample Wallabag entries
    wallabag_entries = [
        {
            "id": 1,
            "url": "https://example.com/article1",
            "given_url": "https://example.com/article1"
        },
        {
            "id": 2,
            "url": "https://example.com/article2",
            "given_url": "https://example.com/article2"
        }
    ]
    
    # Get the URL map
    wallabag_urls = map_entries_to_urls(wallabag_entries)
    
    # Find entries to archive
    entries_to_archive = find_urls_to_archive(set(), wallabag_urls)
    
    # Verify all entries need to be archived
    assert len(entries_to_archive) == 2
    assert set(entries_to_archive) == {1, 2}

def test_find_urls_to_archive_empty_wallabag():
    """Test finding URLs to archive when Wallabag is empty."""
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    
    # Get the URL map
    wallabag_urls = {}  # Empty Wallabag
    
    # Find entries to archive
    entries_to_archive = find_urls_to_archive(set(feed_urls), wallabag_urls)
    
    # Verify no entries need to be archived
    assert len(entries_to_archive) == 0

def test_find_urls_to_archive_no_changes():
    """Test finding URLs to archive when no changes are needed."""
    # Sample feed URLs
    feed_urls = [
        "https://example.com/article1",
        "https://example.com/article2"
    ]
    
    # Sample Wallabag entries (all match feed)
    wallabag_entries = [
        {
            "id": 1,
            "url": "https://example.com/article1",
            "given_url": "https://example.com/article1"
        },
        {
            "id": 2,
            "url": "https://example.com/article2",
            "given_url": "https://example.com/article2"
        }
    ]
    
    # Get the URL map
    wallabag_urls = map_entries_to_urls(wallabag_entries)
    
    # Find entries to archive
    entries_to_archive = find_urls_to_archive(set(feed_urls), wallabag_urls)
    
    # Verify no entries need to be archived
    assert len(entries_to_archive) == 0

def test_add_article_success():
    """Test successful article addition."""
    # Sample response
    response_data = {
        "id": 123,
        "url": "https://example.com/article"
    }
    
    # Mock the requests.post response
    mock_response = Mock()
    mock_response.json.return_value = response_data
    mock_response.status_code = 201  # Created
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.post', return_value=mock_response):
        entry_id = add_article(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            url="https://example.com/article"
        )
        
        # Verify the result
        assert entry_id == 123

def test_add_article_already_exists():
    """Test adding an article that already exists."""
    # Mock the requests.post response
    mock_response = Mock()
    mock_response.status_code = 200  # OK (already exists)
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.post', return_value=mock_response):
        entry_id = add_article(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            url="https://example.com/article"
        )
        
        # Verify the result
        assert entry_id is None

def test_add_article_timeout():
    """Test handling of timeout errors."""
    # Mock requests.post to raise a timeout
    with patch('requests.post', side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            add_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                url="https://example.com/article"
            )
        
        assert "Timeout" in str(exc_info.value)

def test_add_article_http_error():
    """Test handling of HTTP errors."""
    # Mock requests.post to raise an HTTP error
    with patch('requests.post', side_effect=requests.exceptions.HTTPError):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            add_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                url="https://example.com/article"
            )
        
        assert "Error adding article" in str(exc_info.value)

def test_add_article_invalid_response():
    """Test handling of invalid response structure."""
    # Mock response with invalid structure
    mock_response = Mock()
    mock_response.json.return_value = {"url": "https://example.com/article"}  # Missing id
    mock_response.status_code = 201
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.post', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            add_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                url="https://example.com/article"
            )
        
        assert "Invalid response structure" in str(exc_info.value)

def test_add_articles_success():
    """Test successful addition of multiple articles."""
    # Sample responses
    responses = [
        {"id": 1, "url": "https://example.com/article1"},
        {"id": 2, "url": "https://example.com/article2"},
        {"id": 3, "url": "https://example.com/article3"}
    ]
    
    # Create mock responses
    mock_responses = []
    for response in responses:
        mock_response = Mock()
        mock_response.json.return_value = response
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        mock_responses.append(mock_response)
    
    # Test the function with mocked responses
    with patch('requests.post', side_effect=mock_responses):
        added_ids, failed_urls = add_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            urls=[
                "https://example.com/article1",
                "https://example.com/article2",
                "https://example.com/article3"
            ]
        )
        
        # Verify the results
        assert len(added_ids) == 3
        assert added_ids == [1, 2, 3]
        assert len(failed_urls) == 0

def test_add_articles_mixed_results():
    """Test adding articles with mixed success and failure."""
    # First article succeeds, second fails, third succeeds
    mock_responses = [
        Mock(json=lambda: {"id": 1, "url": "https://example.com/article1"},
             status_code=201,
             raise_for_status=lambda: None),
        Mock(side_effect=requests.exceptions.RequestException("Failed")),
        Mock(json=lambda: {"id": 3, "url": "https://example.com/article3"},
             status_code=201,
             raise_for_status=lambda: None)
    ]
    
    # Test the function with mocked responses
    with patch('requests.post', side_effect=mock_responses):
        added_ids, failed_urls = add_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            urls=[
                "https://example.com/article1",
                "https://example.com/article2",
                "https://example.com/article3"
            ]
        )
        
        # Verify the results
        assert len(added_ids) == 2
        assert added_ids == [1, 3]
        assert len(failed_urls) == 1
        assert failed_urls == ["https://example.com/article2"]

def test_add_articles_all_fail():
    """Test adding articles when all fail."""
    # All articles fail
    mock_responses = [
        Mock(side_effect=requests.exceptions.RequestException("Failed")),
        Mock(side_effect=requests.exceptions.RequestException("Failed")),
        Mock(side_effect=requests.exceptions.RequestException("Failed"))
    ]
    
    # Test the function with mocked responses
    with patch('requests.post', side_effect=mock_responses):
        added_ids, failed_urls = add_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            urls=[
                "https://example.com/article1",
                "https://example.com/article2",
                "https://example.com/article3"
            ]
        )
        
        # Verify the results
        assert len(added_ids) == 0
        assert len(failed_urls) == 3
        assert set(failed_urls) == {
            "https://example.com/article1",
            "https://example.com/article2",
            "https://example.com/article3"
        }

def test_add_articles_empty_list():
    """Test adding an empty list of articles."""
    added_ids, failed_urls = add_articles(
        base_url="https://wallabag.example.com",
        access_token="test_token",
        urls=[]
    )
    
    # Verify the results
    assert len(added_ids) == 0
    assert len(failed_urls) == 0

def test_archive_article_success():
    """Test successful article archiving."""
    # Mock the requests.patch response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.patch', return_value=mock_response):
        result = archive_article(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            entry_id=123
        )
        
        # Verify the result
        assert result is True

def test_archive_article_timeout():
    """Test handling of timeout errors."""
    # Mock requests.patch to raise a timeout
    with patch('requests.patch', side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            archive_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                entry_id=123
            )
        
        assert "Timeout" in str(exc_info.value)

def test_archive_article_http_error():
    """Test handling of HTTP errors."""
    # Mock requests.patch to raise an HTTP error
    with patch('requests.patch', side_effect=requests.exceptions.HTTPError):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            archive_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                entry_id=123
            )
        
        assert "Error archiving article" in str(exc_info.value)

def test_archive_article_not_found():
    """Test handling of non-existent article."""
    # Mock response for non-existent article
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    
    # Test the function with mocked response
    with patch('requests.patch', return_value=mock_response):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            archive_article(
                base_url="https://wallabag.example.com",
                access_token="test_token",
                entry_id=999
            )
        
        assert "Error archiving article" in str(exc_info.value)

def test_archive_articles_success():
    """Test successful archiving of multiple articles."""
    # Mock the requests.patch response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.patch', return_value=mock_response):
        archived_ids, failed_ids = archive_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            entry_ids=[1, 2, 3]
        )
        
        # Verify the results
        assert len(archived_ids) == 3
        assert archived_ids == [1, 2, 3]
        assert len(failed_ids) == 0

def test_archive_articles_mixed_results():
    """Test archiving articles with mixed success and failure."""
    # Create a list to track which entry_ids were processed
    processed_ids = []
    
    def mock_patch(*args, **kwargs):
        # Extract entry_id from the URL
        entry_id = int(args[0].split('/')[-1].replace('.json', ''))
        processed_ids.append(entry_id)
        
        # Simulate failure for entry_id 2
        if entry_id == 2:
            raise requests.exceptions.RequestException("Failed")
            
        # For other entries, return success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock(return_value=None)
        return mock_response
    
    # Test the function with mocked responses
    with patch('requests.patch', side_effect=mock_patch):
        archived_ids, failed_ids = archive_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            entry_ids=[1, 2, 3]
        )
        
        # Verify the results
        assert len(archived_ids) == 2
        assert archived_ids == [1, 3]
        assert len(failed_ids) == 1
        assert failed_ids == [2]
        # Verify all entries were processed
        assert set(processed_ids) == {1, 2, 3}

def test_archive_articles_all_fail():
    """Test archiving articles when all fail."""
    # All articles fail
    mock_responses = [
        Mock(side_effect=requests.exceptions.RequestException("Failed")),
        Mock(side_effect=requests.exceptions.RequestException("Failed")),
        Mock(side_effect=requests.exceptions.RequestException("Failed"))
    ]
    
    def mock_patch(*args, **kwargs):
        response = mock_responses.pop(0)
        raise requests.exceptions.RequestException("Failed")
    
    # Test the function with mocked responses
    with patch('requests.patch', side_effect=mock_patch):
        archived_ids, failed_ids = archive_articles(
            base_url="https://wallabag.example.com",
            access_token="test_token",
            entry_ids=[1, 2, 3]
        )
        
        # Verify the results
        assert len(archived_ids) == 0
        assert len(failed_ids) == 3
        assert set(failed_ids) == {1, 2, 3}

def test_archive_articles_empty_list():
    """Test archiving an empty list of articles."""
    archived_ids, failed_ids = archive_articles(
        base_url="https://wallabag.example.com",
        access_token="test_token",
        entry_ids=[]
    )
    
    # Verify the results
    assert len(archived_ids) == 0
    assert len(failed_ids) == 0 