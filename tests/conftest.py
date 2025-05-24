"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = Mock()
    response.json.return_value = {}
    response.status_code = 200
    response.raise_for_status.return_value = None
    return response

@pytest.fixture
def sample_config():
    """Return a sample configuration dictionary."""
    return {
        'FEED_URL': 'http://feed.example.com',
        'WALLABAG_BASE_URL': 'http://wallabag.example.com',
        'WALLABAG_CLIENT_ID': 'client_id',
        'WALLABAG_CLIENT_SECRET': 'client_secret',
        'WALLABAG_USERNAME': 'username',
        'WALLABAG_PASSWORD': 'password'
    }

@pytest.fixture
def sample_entries():
    """Return a sample list of Wallabag entries."""
    return [
        {
            'id': 1,
            'url': 'http://example.com/1',
            'given_url': 'http://example.com/1',
            'hashed_given_url': 'hash1'
        },
        {
            'id': 2,
            'url': 'http://example.com/2',
            'given_url': 'http://example.com/2',
            'hashed_given_url': 'hash2'
        }
    ] 