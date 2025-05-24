🧠 Wallabag Feed Sync Script Architecture

This document describes the full architecture of a script designed to synchronize a public JSON feed of article URLs with a user’s Wallabag “To Read” queue. It includes details on how services connect, where state is stored, and how the script behaves when scheduled with cron.

⸻

📐 High-Level Overview

The script performs the following tasks:
	1.	Fetches a JSON feed of articles from a public URL.
	2.	Parses the feed to extract article URLs.
	3.	Hashes the URLs using SHA1. These hashes will be called "Given URL Hashes".
	4.	Queries the Wallabag API to retrieve the current “To Read” queue.
	5.	Compares the feed URLs to Wallabag entries:
	•	Compare "Given URL Hashes" with Wallabag responses "given_url_hash".
	•	Adds missing URLs to Wallabag.
	•	Archives URLs in Wallabag that are no longer in the feed.

⸻

🧱 Architecture Components

1. Cron Scheduler
	•	Role: Triggers the script at scheduled intervals (e.g., hourly).
	•	Tool: cron on Unix-based systems.

2. Feed Source
	•	Type: Publicly accessible JSON endpoint.
	•	Contents: List of article URLs (expected in a consistent format).

3. Script (Main Logic)
	•	Language: Python, Bash, or similar scripting language.
	•	Responsibilities:
	•	Fetch feed.
	•	Normalize and hash URLs.
	•	Authenticate with Wallabag API.
	•	Compare current state and sync.

4. Wallabag API
	•	Endpoints Used:
	•	GET /api/entries: To list current “To Read” items.
	•	POST /api/entries: To add new articles.
	•	PATCH /api/entries/{id}: To archive articles.

5. State Storage
	•	Method 1: Stateless (Preferred)
	•	Hashes are calculated on the fly during each run.
	•	Wallabag is the source of truth.
	•	No persistent state needed.
	•	Method 2: Cached State File (Optional)
	•	Store last known feed SHA1 hashes in a file (e.g., last_feed.json) to avoid unnecessary API calls.
	•	Tradeoff: Additional complexity and file locking concerns.

⸻

🔗 Data Flow Diagram

graph TD;
    cron[cron schedule]
    script[Sync Script]
    feed[Public JSON Feed]
    wallabag[Wallabag API]
    
    cron --> script
    script --> feed
    script --> wallabag
    wallabag --> script


⸻

🧾 Example Script Flow (Stateless)
	1.	Start: Script runs via cron.
	2.	Fetch Feed: GET request to JSON feed URL.
	3.	Parse & Hash: Extract URLs and hash them with SHA1.
	4.	Fetch Wallabag Entries: GET /api/entries?archive=0&detail=metadata&perPage=500.
	5.	Compare:
	•	Add articles in feed but not in Wallabag.
	•	Archive articles in Wallabag not in the feed.
	6.	End.

⸻

🔐 Authentication

Wallabag requires OAuth2 tokens:
	•	access_token: Used for API requests.
	•	refresh_token: Used to obtain a new access token.
	•	Store these securely (e.g., in .env, or config file with proper permissions).

⸻

📦 Environment/Config

FEED_URL=https://example.com/feed.json
WALLABAG_BASE_URL=https://wallabag.example.com
WALLABAG_CLIENT_ID=your_client_id
WALLABAG_CLIENT_SECRET=your_client_secret
WALLABAG_USERNAME=your_username
WALLABAG_PASSWORD=your_password


⸻

📋 Cron Example

# Run every hour
0 * * * * /usr/bin/python3 /path/to/wallabag_sync.py >> /var/log/wallabag_sync.log 2>&1


⸻

📈 Optional Enhancements
	•	Logging: Store actions (added/archived URLs) in a log file.
	•	Retry logic for failed API calls.
	•	Error reporting via email, webhook, or push notification.
	•	Unit tests for the hashing and comparison logic.

⸻

✅ Summary

This script enables automated curation of Wallabag reading material by keeping it in sync with a dynamic feed. It avoids state persistence by relying on hashing and API queries, making it simple, robust, and cron-friendly.

⸻
