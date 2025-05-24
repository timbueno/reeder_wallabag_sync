import json
import pytest
import requests
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from wallabag_sync.feed import fetch_feed, extract_urls

def test_fetch_feed_success():
    """Test successful feed fetching and parsing."""
    # Sample feed data
    sample_feed = {
        "items": [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"}
        ]
    }
    
    # Mock the requests.get response
    mock_response = Mock()
    mock_response.json.return_value = sample_feed
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.get', return_value=mock_response):
        result = fetch_feed("https://example.com/feed.json")
        
        # Verify the result
        assert result == sample_feed
        assert "items" in result
        assert len(result["items"]) == 2

def test_fetch_feed_timeout():
    """Test handling of timeout errors."""
    # Mock requests.get to raise a timeout
    with patch('requests.get', side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            fetch_feed("https://example.com/feed.json")
        
        assert "Timeout" in str(exc_info.value)

def test_fetch_feed_invalid_json():
    """Test handling of invalid JSON responses."""
    # Mock response with invalid JSON
    mock_response = Mock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status.return_value = None
    
    # Test the function with mocked response
    with patch('requests.get', return_value=mock_response):
        with pytest.raises(ValueError) as exc_info:
            fetch_feed("https://example.com/feed.json")
        
        assert "Invalid JSON" in str(exc_info.value)

def test_fetch_feed_http_error():
    """Test handling of HTTP errors."""
    # Mock requests.get to raise an HTTP error
    with patch('requests.get', side_effect=requests.exceptions.HTTPError):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            fetch_feed("https://example.com/feed.json")
        
        assert "Error fetching feed" in str(exc_info.value)

def test_extract_urls_success():
    """Test successful URL extraction from feed data."""
    # Sample feed data
    feed_data = {
        "items": [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"},
            {"title": "No URL item"},  # Should be skipped
            {"url": "https://example.com/3"}
        ]
    }
    
    # Extract URLs
    urls = extract_urls(feed_data)
    
    # Verify results
    assert len(urls) == 3
    assert "https://example.com/1" in urls
    assert "https://example.com/2" in urls
    assert "https://example.com/3" in urls

def test_extract_urls_missing_items():
    """Test handling of feed data missing items field."""
    # Feed data without items
    feed_data = {"title": "Test Feed"}
    
    # Verify ValueError is raised
    with pytest.raises(ValueError) as exc_info:
        extract_urls(feed_data)
    
    assert "missing 'items' field" in str(exc_info.value)

def test_extract_urls_invalid_structure():
    """Test handling of invalid feed data structure."""
    # Invalid feed data (items is not a list)
    feed_data = {"items": "not a list"}
    
    # Verify ValueError is raised
    with pytest.raises(ValueError) as exc_info:
        extract_urls(feed_data)
    
    assert "must be a list" in str(exc_info.value) 