✅ Wallabag Feed Sync MVP – Task List

⸻

🧱 Setup Tasks

1. ✅ Initialize a new project directory
	•	Start: No folder exists yet.
	•	End: Project folder created with a README.md and .gitignore.

⸻

2. ✅ Create a .env file to store configuration values
	•	Start: .env does not exist.
	•	End: .env file created with placeholder variables:

FEED_URL=
WALLABAG_BASE_URL=
WALLABAG_CLIENT_ID=
WALLABAG_CLIENT_SECRET=
WALLABAG_USERNAME=
WALLABAG_PASSWORD=



⸻

3. ✅ Write a function to load environment variables
	•	Start: Project has no configuration loading.
	•	End: load_config() function that returns a dict of config values from .env.

⸻

📥 Feed Fetching Tasks

4. ✅ Write a function to fetch the JSON feed
	•	Start: No feed retrieval logic.
	•	End: Function fetch_feed() returns parsed JSON from the configured FEED_URL.

⸻

5. ✅ Write a function to extract article URLs from feed
	•	Start: JSON feed is a raw list or object.
	•	End: extract_urls(feed_json) returns a List[str] of article URLs.

⸻

🔐 Wallabag Auth Tasks

6. ✅ Write a function to request an access token from Wallabag
	•	Start: No authentication logic.
	•	End: get_access_token() sends a POST to /oauth/v2/token and returns access_token.

⸻

📚 Wallabag Entry Management Tasks

7. ✅ Write a function to fetch current unread Wallabag entries
	•	Start: No Wallabag entries are fetched.
	•	End: get_unread_entries(token) returns a list of {"id": ..., "url": ...}.

⸻

8. ✅ Write a function to hash a URL using SHA1
	•	Start: No hashing implemented.
	•	End: hash_url(url: str) -> str returns a SHA1 hash of a URL string.

⸻

9. ✅ Write a function to map Wallabag entries to hashed URLs
	•	Start: Entries are in raw list format.
	•	End: Function returns Dict[str, int] of {sha1_hash: wallabag_id}.

⸻

10. ✅ Write a function to find new URLs to add
	•	Start: Two URL lists exist.
	•	End: find_urls_to_add(feed_urls, wallabag_hashes) returns a list of str.

⸻

11. ✅ Write a function to find URLs to archive
	•	Start: Two URL lists exist.
	•	End: find_urls_to_archive(feed_hashes, wallabag_hashes) returns a list of wallabag_ids.

⸻

➕ Adding Articles

12. ✅ Write a function to add an article to Wallabag
	•	Start: No POST logic exists.
	•	End: add_article(url, token) sends a POST to /api/entries.json and handles success/failure.

⸻

13. ✅ Write a loop to add all new articles
	•	Start: List of URLs to add exists.
	•	End: All new URLs are added using add_article().

⸻

🗃️ Archiving Articles

14. ✅ Write a function to archive an article in Wallabag
	•	Start: No PATCH logic exists.
	•	End: archive_article(entry_id, token) sends PATCH request to archive it.

⸻

15. ✅ Write a loop to archive all outdated articles
	•	Start: List of entry IDs to archive exists.
	•	End: All outdated articles are archived using archive_article().

⸻

🧪 Testing & CLI Integration

16. ✅ Write a main() function to call all steps in order
	•	Start: All functions exist but not connected.
	•	End: main() implements the full flow:
	•	Load config
	•	Get access token
	•	Fetch & extract feed
	•	Fetch Wallabag entries
	•	Compare
	•	Add missing
	•	Archive stale

⸻

17. ✅ Add CLI guard and logging output
	•	Start: No CLI entry point exists.
	•	End: Script prints progress and has:

if __name__ == "__main__":
    main()



⸻

18. ✅ Test full script manually with dummy or real credentials
	•	Start: Script ready for trial.
	•	End: Manually run and verify:
	•	Adds new articles
	•	Archives stale ones
	•	Logs actions

⸻

19. ✅ Write a basic cron-safe shell wrapper
	•	Start: Script runs only manually.
	•	End: wallabag_sync.sh created to activate virtualenv and run the script.

⸻

20. ✅ Set up cron job
	•	Start: Script is not scheduled.
	•	End: Crontab entry like:

0 * * * * /path/to/wallabag_sync.sh
