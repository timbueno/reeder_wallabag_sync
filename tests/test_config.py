import os
import pytest
from unittest.mock import patch
from wallabag_sync.config import load_config

def test_load_config_success():
    """Test successful loading of all environment variables."""
    # Set up test environment variables
    test_config = {
        'FEED_URL': 'https://example.com/feed.json',
        'WALLABAG_BASE_URL': 'https://wallabag.example.com',
        'WALLABAG_CLIENT_ID': 'test_client_id',
        'WALLABAG_CLIENT_SECRET': 'test_client_secret',
        'WALLABAG_USERNAME': 'test_user',
        'WALLABAG_PASSWORD': 'test_password'
    }
    
    # Set environment variables for testing
    for key, value in test_config.items():
        os.environ[key] = value
    
    try:
        # Load config without loading .env file
        config = load_config(load_env_file=False)
        
        # Verify all values are loaded correctly
        assert config == test_config
        
        # Verify all required keys are present
        assert all(key in config for key in test_config.keys())
        
    finally:
        # Clean up environment variables
        for key in test_config.keys():
            os.environ.pop(key, None)

def test_load_config_missing_variable():
    """Test that ValueError is raised when a required variable is missing."""
    # Set up test environment variables with one missing
    test_config = {
        'FEED_URL': 'https://example.com/feed.json',
        'WALLABAG_BASE_URL': 'https://wallabag.example.com',
        'WALLABAG_CLIENT_ID': 'test_client_id',
        'WALLABAG_CLIENT_SECRET': 'test_client_secret',
        'WALLABAG_USERNAME': 'test_user',
        # WALLABAG_PASSWORD is intentionally missing
    }
    
    # Set environment variables for testing
    for key, value in test_config.items():
        os.environ[key] = value
    
    try:
        # Verify that ValueError is raised when loading without .env file
        with pytest.raises(ValueError) as exc_info:
            load_config(load_env_file=False)
        
        # Verify the error message mentions the missing variable
        assert "Missing required environment variable: WALLABAG_PASSWORD" in str(exc_info.value)
        
    finally:
        # Clean up environment variables
        for key in test_config.keys():
            os.environ.pop(key, None) 