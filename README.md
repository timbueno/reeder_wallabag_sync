# Wallabag Sync

A Python tool to synchronize a JSON feed with your Wallabag instance. This tool helps you keep your Wallabag reading list in sync with a feed of articles.

## Features

- Fetches articles from a JSON feed
- Adds new articles to Wallabag
- Archives articles that are no longer in the feed
- Handles duplicate URLs gracefully
- Configurable via environment variables

## Installation

```bash
pip install wallabag-sync
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file in the root directory of your project with your configuration:
```env
FEED_URL=https://example.com/feed.json
WALLABAG_BASE_URL=https://wallabag.example.com
WALLABAG_CLIENT_ID=your_client_id
WALLABAG_CLIENT_SECRET=your_client_secret
WALLABAG_USERNAME=your_username
WALLABAG_PASSWORD=your_password
```

## Usage

Run the sync tool:

```bash
wallabag-sync
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wallabag_sync.git
cd wallabag_sync
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Copy and configure the environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run tests:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 