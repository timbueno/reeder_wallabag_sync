"""Tests for the CLI module."""

import pytest
from unittest.mock import patch, Mock
from requests.exceptions import RequestException
from wallabag_sync.cli import main
import os

def test_main_success():
    """Test successful execution of the main function."""
    # Mock environment variables
    env_patch = patch.dict('os.environ', {
        'FEED_URL': 'http://feed.example.com',
        'WALLABAG_BASE_URL': 'http://wallabag.example.com',
        'WALLABAG_CLIENT_ID': 'client_id',
        'WALLABAG_CLIENT_SECRET': 'client_secret',
        'WALLABAG_USERNAME': 'username',
        'WALLABAG_PASSWORD': 'password'
    })
    
    # Mock all required functions
    load_config_patch = patch('wallabag_sync.cli.load_config')
    fetch_feed_patch = patch('wallabag_sync.cli.fetch_feed')
    extract_urls_patch = patch('wallabag_sync.cli.extract_urls')
    get_token_patch = patch('wallabag_sync.cli.get_access_token')
    get_entries_patch = patch('wallabag_sync.cli.get_unread_entries')
    add_articles_patch = patch('wallabag_sync.cli.add_articles')
    archive_articles_patch = patch('wallabag_sync.cli.archive_articles')
    exit_patch = patch('sys.exit')
    
    with env_patch, \
         load_config_patch as mock_load_config, \
         fetch_feed_patch as mock_fetch_feed, \
         extract_urls_patch as mock_extract_urls, \
         get_token_patch as mock_get_token, \
         get_entries_patch as mock_get_entries, \
         add_articles_patch as mock_add_articles, \
         archive_articles_patch as mock_archive_articles, \
         exit_patch as mock_exit:
        
        # Mock configuration
        mock_load_config.return_value = {
            'FEED_URL': 'http://feed.example.com',
            'WALLABAG_BASE_URL': 'http://wallabag.example.com',
            'WALLABAG_CLIENT_ID': 'client_id',
            'WALLABAG_CLIENT_SECRET': 'client_secret',
            'WALLABAG_USERNAME': 'username',
            'WALLABAG_PASSWORD': 'password'
        }
        
        # Mock feed data
        mock_fetch_feed.return_value = {'items': []}
        mock_extract_urls.return_value = [
            'http://example.com/1',
            'http://example.com/2'
        ]
        
        # Mock access token
        mock_get_token.return_value = 'access_token'
        
        # Mock Wallabag entries - include an entry that should be archived
        mock_get_entries.return_value = [
            {
                'id': 1,
                'url': 'http://example.com/1',
                'given_url': 'http://example.com/1',
                'hashed_given_url': 'hash1'
            },
            {
                'id': 3,
                'url': 'http://example.com/3',  # This URL is not in the feed
                'given_url': 'http://example.com/3',
                'hashed_given_url': 'hash3'
            }
        ]
        
        # Mock article operations
        mock_add_articles.return_value = ([2], [])  # One article added successfully
        mock_archive_articles.return_value = ([3], [])  # One article archived successfully
        
        # Run main function
        main()
        
        # Verify function calls
        mock_load_config.assert_called_once()
        mock_fetch_feed.assert_called_once_with('http://feed.example.com')
        mock_extract_urls.assert_called_once()
        mock_get_token.assert_called_once()
        mock_get_entries.assert_called_once()
        mock_add_articles.assert_called_once()
        mock_archive_articles.assert_called_once_with(
            base_url='http://wallabag.example.com',
            access_token='access_token',
            entry_ids=[3]  # Entry 3 should be archived
        )
        
        # Verify sys.exit was called with success code
        mock_exit.assert_called_once_with(0)

def test_main_missing_config():
    """Test main function with missing configuration."""
    # Mock environment variables
    env_patch = patch.dict('os.environ', {}, clear=True)
    
    # Mock required functions
    load_config_patch = patch('wallabag_sync.cli.load_config')
    exit_patch = patch('sys.exit')
    
    with env_patch, \
         load_config_patch as mock_load_config, \
         exit_patch as mock_exit:
        
        # Mock missing configuration
        mock_load_config.side_effect = KeyError('WALLABAG_BASE_URL')
        
        # Run main function
        main()
        
        # Verify sys.exit was called with error code
        mock_exit.assert_called_once_with(1)

def test_main_feed_error():
    """Test main function with feed fetch error."""
    with patch.dict('os.environ', {
        'FEED_URL': 'http://feed.example.com',
        'WALLABAG_BASE_URL': 'http://wallabag.example.com',
        'WALLABAG_CLIENT_ID': 'client_id',
        'WALLABAG_CLIENT_SECRET': 'client_secret',
        'WALLABAG_USERNAME': 'username',
        'WALLABAG_PASSWORD': 'password'
    }), \
    patch('wallabag_sync.cli.load_config') as mock_load_config, \
    patch('wallabag_sync.cli.fetch_feed') as mock_fetch_feed, \
    patch('wallabag_sync.cli.get_access_token') as mock_get_token, \
    patch('sys.exit') as mock_exit:
        
        # Mock configuration
        mock_load_config.return_value = {
            'FEED_URL': 'http://feed.example.com',
            'WALLABAG_BASE_URL': 'http://wallabag.example.com',
            'WALLABAG_CLIENT_ID': 'client_id',
            'WALLABAG_CLIENT_SECRET': 'client_secret',
            'WALLABAG_USERNAME': 'username',
            'WALLABAG_PASSWORD': 'password'
        }
        
        # Mock access token
        mock_get_token.return_value = 'access_token'
        
        # Mock feed fetch error
        mock_fetch_feed.side_effect = RequestException("Failed to fetch feed")
        
        # Run main function
        main()
        
        # Verify sys.exit was called with error code
        mock_exit.assert_called_once_with(1) 