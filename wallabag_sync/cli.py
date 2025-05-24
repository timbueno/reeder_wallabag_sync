"""Command-line interface for Wallabag Feed Sync."""

import sys
from typing import Dict, List

from wallabag_sync.wallabag import (
    get_access_token,
    get_unread_entries,
    map_entries_to_urls,
    find_urls_to_add,
    find_urls_to_archive,
    add_articles,
    archive_articles
)
from wallabag_sync.utils import load_config
from wallabag_sync.feed import fetch_feed, extract_urls
from requests.exceptions import RequestException

def main() -> None:
    """Main function to synchronize Wallabag entries with the feed.
    
    This function:
    1. Loads configuration from environment variables
    2. Gets an access token from Wallabag
    3. Fetches and extracts URLs from the feed
    4. Fetches current unread entries from Wallabag
    5. Compares feed URLs with Wallabag entries
    6. Adds missing URLs to Wallabag
    7. Archives entries that are no longer in the feed
    
    Raises:
        KeyError: If required environment variables are missing
        RequestException: If there are network errors
        Exception: For any other unexpected errors
    """
    try:
        print("Starting Wallabag feed sync...")
        
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully")
        
        # Get access token
        print("Requesting access token...")
        access_token = get_access_token(
            base_url=config['WALLABAG_BASE_URL'],
            client_id=config['WALLABAG_CLIENT_ID'],
            client_secret=config['WALLABAG_CLIENT_SECRET'],
            username=config['WALLABAG_USERNAME'],
            password=config['WALLABAG_PASSWORD']
        )
        print("Access token obtained successfully")
        
        # Fetch and extract feed URLs
        print(f"Fetching feed from {config['FEED_URL']}...")
        feed_data = fetch_feed(config['FEED_URL'])
        feed_urls = extract_urls(feed_data)
        print(f"Found {len(feed_urls)} URLs in feed")
        print("\nFeed URLs:")
        for url in feed_urls:
            print(f"  - {url}")
        
        # Fetch current unread entries from Wallabag
        print("\nFetching current unread entries from Wallabag...")
        entries = get_unread_entries(
            base_url=config['WALLABAG_BASE_URL'],
            access_token=access_token
        )
        print(f"Found {len(entries)} unread entries in Wallabag")
        print("\nWallabag entries:")
        for entry in entries:
            print(f"  - ID: {entry['id']}")
            print(f"    URL: {entry['url']}")
            print(f"    Given URL: {entry['given_url']}")
        
        # Map entries to URLs
        wallabag_urls = map_entries_to_urls(entries)
        print("\nWallabag URL map:")
        for url, entry_id in wallabag_urls.items():
            print(f"  - URL: {url} -> Entry ID: {entry_id}")
        
        # Find URLs to add and archive
        urls_to_add = find_urls_to_add(feed_urls, wallabag_urls)
        entries_to_archive = find_urls_to_archive(set(feed_urls), wallabag_urls)
        
        print(f"\nFound {len(urls_to_add)} new URLs to add")
        if urls_to_add:
            print("URLs to add:")
            for url in urls_to_add:
                print(f"  - {url}")
        
        print(f"\nFound {len(entries_to_archive)} entries to archive")
        if entries_to_archive:
            print("Entries to archive:")
            for entry_id in entries_to_archive:
                # Find the entry details for better logging
                entry = next((e for e in entries if e['id'] == entry_id), None)
                if entry:
                    print(f"  - ID: {entry_id}")
                    print(f"    URL: {entry['url']}")
                    print(f"    Given URL: {entry['given_url']}")
                else:
                    print(f"  - ID: {entry_id} (details not found)")
        
        # Add missing URLs
        if urls_to_add:
            print("\nAdding new articles to Wallabag...")
            added_ids, failed_urls = add_articles(
                base_url=config['WALLABAG_BASE_URL'],
                access_token=access_token,
                urls=urls_to_add
            )
            print(f"Successfully added {len(added_ids)} new articles")
            if failed_urls:
                print(f"Failed to add {len(failed_urls)} articles:")
                for url in failed_urls:
                    print(f"  - {url}")
        
        # Archive stale entries
        if entries_to_archive:
            print("\nArchiving stale entries...")
            archived_ids, failed_ids = archive_articles(
                base_url=config['WALLABAG_BASE_URL'],
                access_token=access_token,
                entry_ids=entries_to_archive
            )
            print(f"Successfully archived {len(archived_ids)} articles")
            if failed_ids:
                print(f"Failed to archive {len(failed_ids)} articles:")
                for entry_id in failed_ids:
                    print(f"  - Entry ID: {entry_id}")
        
        print("\nSync completed successfully")
        sys.exit(0)  # Explicitly exit with success code
        
    except KeyError as e:
        print(f"Error: Missing required environment variable: {e}")
        sys.exit(1)
    except RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 