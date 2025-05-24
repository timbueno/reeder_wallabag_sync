"""Wallabag Feed Sync package."""

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

__all__ = [
    'get_access_token',
    'get_unread_entries',
    'map_entries_to_urls',
    'find_urls_to_add',
    'find_urls_to_archive',
    'add_article',
    'add_articles',
    'archive_article',
    'archive_articles'
]

__version__ = "0.1.0" 