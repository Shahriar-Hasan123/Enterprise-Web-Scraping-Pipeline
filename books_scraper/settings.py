# books_scraper/settings.py

from pathlib import Path

# -----PATH CONFIGURATION-----

# Root directory of the project (where scrapy.cfg lives)
BASE_DIR = Path(__file__).resolve().parent.parent

# -----PROJECT IDENTITY-----

BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"

# -----CRAWLING BEHAVIOR-----

# Respect the website's robots.txt rules
ROBOTSTXT_OBEY = True

# Pause between requests (in seconds) — be polite to the server
DOWNLOAD_DELAY = 1

# Maximum concurrent requests to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Default request headers — identify ourselves professionally
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

# -----ITEM PIPELINES-----

# Lower number = runs first
# DataCleaningPipeline must run BEFORE SQLitePipeline

ITEM_PIPELINES = {
    "books_scraper.pipelines.DataCleaningPipeline": 100,
    "books_scraper.pipelines.SQLitePipeline": 200,
}


# -----FEED EXPORTS — Export scraped data to files-----

# All three formats export identical data
# Files are saved inside the data/ folder

FEEDS = {
    # JSON export
    BASE_DIR / "data" / "books.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": 4,          # Pretty print with 4-space indentation
        "overwrite": True,    # Overwrite file on each run (no duplicates)
    },

    # CSV export
    BASE_DIR / "data" / "books.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "overwrite": True,
    },

    # XML export
    BASE_DIR / "data" / "books.xml": {
        "format": "xml",
        "encoding": "utf-8",
        "overwrite": True,
    },
}

# -----LOGGING-----

# Log level — INFO shows important events, hides debug noise
LOG_LEVEL = "INFO"

# -----PERFORMANCE & ENCODING-----

# Encoding for all requests
FEED_EXPORT_ENCODING = "utf-8"

# Enable AutoThrottle — automatically adjusts delay based on server response
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# -----SCRAPY INTERNALS (leave these as recommended defaults)-----

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"