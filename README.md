# 📚 Enterprise Web Scraping Pipeline — Books Data Engineering System

A production-ready Scrapy application that dynamically crawls [books.toscrape.com](https://books.toscrape.com), processes and cleans book data through an item pipeline, exports results in multiple formats, stores records in SQLite, and deploys via Scrapyd inside a Docker container.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Architecture Diagram](#-architecture-diagram)
- [Installation Guide](#-installation-guide)
- [Environment Setup](#-environment-setup)
- [Running the Spider](#-running-the-spider)
- [Output Format Description](#-output-format-description)
- [Database Configuration](#-database-configuration)
- [Docker Setup Guide](#-docker-setup-guide)
- [Scrapyd Deployment Guide](#-scrapyd-deployment-guide)
- [Design Decisions](#-design-decisions)
- [Known Limitations](#-known-limitations)

---

## 🔎 Project Overview

This project implements a fully automated web scraping pipeline targeting [books.toscrape.com](https://books.toscrape.com). It demonstrates professional-grade Scrapy development including dynamic crawling, data cleaning, multi-format exports, SQLite persistence, containerization with Docker, and remote spider management with Scrapyd.

The spider:
1. Starts from the homepage and dynamically discovers all book categories
2. Randomly selects **5 categories** without any hardcoded URLs or names
3. Collects **all books** across all pages of each selected category (pagination handled)
4. Randomly selects **5 books** per category (25 books total per run)
5. Extracts full book details from each book's detail page
6. Cleans and normalizes all data through a pipeline
7. Exports to JSON, CSV, and XML simultaneously
8. Persists all records to a SQLite database

---

## ✨ Features

- ✅ Dynamic category discovery — zero hardcoded URLs or category names
- ✅ Full pagination support across all category pages
- ✅ Random category and book selection using `random.sample()`
- ✅ Dual selector usage — both CSS and XPath selectors throughout
- ✅ Data cleaning pipeline — whitespace trimming, price normalization, availability as boolean
- ✅ Multi-format export — JSON, CSV, and XML via Scrapy Feed Exports
- ✅ SQLite persistence via Scrapy Item Pipeline
- ✅ Data integrity — identical records across all output formats and database
- ✅ Fully containerized with Docker
- ✅ Remote spider management via Scrapyd API
- ✅ AutoThrottle enabled — polite, adaptive request pacing
- ✅ Comprehensive logging throughout crawling, processing, and storage
- ✅ OOP, SOLID, and DRY principles applied throughout
- ✅ Docstrings on every class and method

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core language |
| Scrapy | Web scraping framework |
| Scrapyd | Spider deployment and scheduling server |
| scrapyd-client | CLI tool to deploy spiders to Scrapyd |
| SQLite | Lightweight database for persistent storage |
| Docker | Containerization and deployment |
| itemadapter | Safe item field access in pipelines |

*See `requirements.txt` for all dependency versions.*

---

## 📁 Folder Structure

```
books_scraper/                      ← Project root
├── books_scraper/                  ← Scrapy Python package
│   ├── spiders/
│   │   ├── __init__.py
│   │   └── books_spider.py         ← Core spider logic
│   ├── __init__.py
│   ├── items.py                    ← BookItem data schema
│   ├── middlewares.py              ← Scrapy middleware (default)
│   ├── pipelines.py                ← Data cleaning + SQLite pipeline
│   └── settings.py                 ← All project configuration
├── data/                           ← Exported output files (generated at runtime)
│   ├── books.json
│   ├── books.csv
│   └── books.xml
├── database/                       ← SQLite database (generated at runtime)
│   └── books.db
├── logs/                           ← Spider run logs
├── .dockerignore                   ← Files excluded from Docker build
├── .gitignore                      ← Files excluded from Git
├── Dockerfile                      ← Docker image definition
├── scrapyd.conf                    ← Scrapyd server configuration
├── scrapy.cfg                      ← Scrapy + Scrapyd deploy configuration
├── requirements.txt                ← Python dependencies
└── README.md                       ← Project documentation
```

---

## 🏗 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCKER CONTAINER                         │
│                                                                 │
│  ┌──────────┐    deploy     ┌─────────────────────────────────┐ │
│  │ scrapy   │ ────────────► │         SCRAPYD SERVER          │ │
│  │ .cfg     │               │         (port 6800)             │ │
│  └──────────┘               └──────────────┬────────────────--┘ │
│                                            │ schedules          │
│                                            ▼                    │
│                             ┌──────────────────────────────┐    │
│                             │        BooksSpider           │    │
│                             │                              │    │
│                             │  parse()                     │    │
│                             │    └─► discover categories   │    │
│                             │         └─► random 5 picked  │    │
│                             │                              │    │
│                             │  parse_category()            │    │
│                             │    └─► collect all books     │    │
│                             │         └─► pagination loop  │    │
│                             │              └─► random 5    │    │
│                             │                              │    │
│                             │  parse_book()                │    │
│                             │    └─► extract 6 fields      │    │
│                             └──────────────┬───────────────┘    │
│                                            │ yields BookItem    │
│                                            ▼                    │
│                             ┌──────────────────────────────┐    │
│                             │    DataCleaningPipeline      │    │
│                             │  · strip whitespace          │    │
│                             │  · price → float             │    │
│                             │  · availability → bool       │    │
│                             └──────────────┬───────────────┘    │
│                                            │                    │
│                                            ▼                    │
│                             ┌──────────────────────────────┐    │
│                             │       SQLitePipeline         │    │
│                             │  · INSERT into books table   │    │
│                             └──────────────┬───────────────┘    │
│                                            │                    │
│                          ┌─────────────────┼──────────────┐     │
│                          ▼                 ▼              ▼     │
│                    ┌──────────┐     ┌──────────┐  ┌────────────┐│
│                    │books.json│     │books.csv │  │ books.xml  ││
│                    └──────────┘     └──────────┘  └────────────┘│
│                                                                 │
│                    ┌─────────────────────┐                      │
│                    │   database/books.db │                      │
│                    └─────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
         ▲
         │  curl API calls
         │
  ┌──────────────┐
  │  Your Machine│
  │  (host)      │
  └──────────────┘
```

---

## 📦 Installation Guide

### Prerequisites

Make sure you have the following installed on your machine:

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)
- Git

### Clone the repository

```bash
git clone https://github.com/Shahriar-Hasan123/Enterprise-Web-Scraping-Pipeline.git
cd books_scraper
```

---

## ⚙️ Environment Setup

### 1. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate — Linux/Mac
source .venv/bin/activate

# Activate — Windows
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Scrapy installation

```bash
scrapy version
# Expected: Scrapy 2.16.0

scrapy list
# Expected: (no spiders yet until you deploy)
```

---

## 🕷 Running the Spider

### Option A — Run directly with Scrapy (local, no Docker)

```bash
# Run spider — outputs to data/ and database/
scrapy crawl books
```

### Option B — Run via Scrapyd API (inside Docker)

See [Scrapyd Deployment Guide](#-scrapyd-deployment-guide) below.

### Verify output after running

```bash
# Check exported files
ls data/

# Preview JSON output
cat data/books.json

# Check database records
python -c "
import sqlite3
conn = sqlite3.connect('database/books.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM books')
print('Total records:', cursor.fetchone()[0])
cursor.execute('SELECT title, price, availability, category FROM books LIMIT 5')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

Expected: **25 records** (5 categories × 5 books each)

---

## 📄 Output Format Description

All three export formats contain identical data with the same 6 fields.

### Fields

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `title` | string | `"A Light in the Attic"` | Book title (whitespace trimmed) |
| `price` | float | `51.77` | Price as number, currency symbol removed |
| `availability` | boolean | `true` | `true` = In stock, `false` = Out of stock |
| `product_url` | string | `"https://books.toscrape.com/..."` | Full URL to book detail page |
| `image_url` | string | `"https://books.toscrape.com/media/..."` | Full URL to book cover image |
| `category` | string | `"Mystery"` | Category the book belongs to |

### books.json

Pretty-printed JSON array with 4-space indentation. UTF-8 encoded. Overwritten on each run.

```json
[
    {
        "title": "A Light in the Attic",
        "price": 51.77,
        "availability": true,
        "product_url": "https://books.toscrape.com/catalogue/...",
        "image_url": "https://books.toscrape.com/media/cache/...",
        "category": "Poetry"
    }
]
```

### books.csv

Standard CSV with header row. UTF-8 encoded. Overwritten on each run.

```
title,price,availability,product_url,image_url,category
A Light in the Attic,51.77,True,https://...,https://...,Poetry
```

### books.xml

Standard XML with one `<item>` element per book. UTF-8 encoded. Overwritten on each run.

```xml
<?xml version="1.0" encoding="utf-8"?>
<items>
    <item>
        <title>A Light in the Attic</title>
        <price>51.77</price>
        <availability>True</availability>
        ...
    </item>
</items>
```

---

## 🗄 Database Configuration

### Engine
SQLite (built into Python — no installation required)

### Location
```
database/books.db
```

### Table Schema

```sql
CREATE TABLE IF NOT EXISTS books (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    price        REAL    NOT NULL,
    availability INTEGER NOT NULL,   -- 1 = In stock, 0 = Out of stock
    product_url  TEXT    NOT NULL,
    image_url    TEXT    NOT NULL,
    category     TEXT    NOT NULL
);
```

### Querying the database

```bash
# Open SQLite shell
sqlite3 database/books.db

# Inside SQLite shell:
.headers on
.mode column
SELECT * FROM books LIMIT 10;
SELECT COUNT(*) FROM books;
SELECT category, COUNT(*) FROM books GROUP BY category;
.quit
```

---

## 🐳 Docker Setup Guide

### 1. Build the Docker image

```bash
docker build -t books-scraper .
```

### 2. Run the container

```bash
docker run -d \
  --name books-scraper-container \
  -p 6800:6800 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/database:/app/database \
  books-scraper
```

### Pull from Docker Hub (recommended)

Instead of building locally, pull the pre-built image directly:

```bash
docker pull shahriar123/books-scraper:latest
```

Then run:

```bash
docker run -d \
  --name books-scraper-container \
  -p 6800:6800 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/database:/app/database \
  shahriar123/books-scraper:latest
```

| Flag | Purpose |
|------|---------|
| `-d` | Run in background (detached mode) |
| `--name` | Give the container a friendly name |
| `-p 6800:6800` | Map Scrapyd port to your machine |
| `-v $(pwd)/data:/app/data` | Mount local data/ so output files appear on your machine |
| `-v $(pwd)/database:/app/database` | Mount local database/ so books.db appears on your machine |

### 3. Verify container is running

```bash
docker ps
```

### 4. Verify Scrapyd is alive

```bash
curl http://localhost:6800/daemonstatus.json
```

Expected:
```json
{"status": "ok", "running": 0, "pending": 0, "finished": 0, "node_name": "..."}
```

### 5. View container logs

```bash
docker logs books-scraper-container
```

### 6. Stop and remove the container

```bash
docker stop books-scraper-container
docker rm books-scraper-container
```

---

## 🚀 Scrapyd Deployment Guide

Scrapyd is a service that manages Scrapy spiders via an HTTP API. Instead of running `scrapy crawl` manually, you deploy the spider once and trigger it via API calls.

### Step 1 — Ensure container is running

```bash
curl http://localhost:6800/daemonstatus.json
# Must return: {"status": "ok", ...}
```

### Step 2 — Deploy the spider

Run from your project root with the virtual environment active:

```bash
scrapyd-deploy local -p books_scraper
```

Expected:
```json
{"status": "ok", "project": "books_scraper", "version": "1234567890", "spiders": 1}
```

### Step 3 — Schedule a spider run

```bash
curl http://localhost:6800/schedule.json \
  -d project=books_scraper \
  -d spider=books
```

Expected:
```json
{"status": "ok", "jobid": "some-unique-job-id", "node_name": "..."}
```

### Step 4 — Monitor the job

```bash
curl http://localhost:6800/listjobs.json?project=books_scraper
```

Response shows `pending`, `running`, and `finished` jobs.

### Step 5 — List available spiders

```bash
curl http://localhost:6800/listspiders.json?project=books_scraper
```

### Scrapyd API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/daemonstatus.json` | GET | Check if Scrapyd is running |
| `/schedule.json` | POST | Schedule a spider run |
| `/cancel.json` | POST | Cancel a running job |
| `/listprojects.json` | GET | List all deployed projects |
| `/listspiders.json` | GET | List spiders in a project |
| `/listjobs.json` | GET | List pending/running/finished jobs |

---

## 🧠 Design Decisions

**1. Random selection at category level, not just book level**
The assignment requires exactly 5 books per category. By selecting categories first and then books within each category, we guarantee an even distribution across different genres — rather than 25 books all from one popular category.

**2. Pagination before random selection**
All book URLs within a category are collected across all pages before random selection. This ensures every book in the category has an equal chance of being selected — not just books from page 1.

**3. Two separate pipelines**
`DataCleaningPipeline` and `SQLitePipeline` are kept separate following the Single Responsibility Principle. Cleaning logic is independent of storage logic — either can be modified or replaced without touching the other.

**4. `ItemAdapter` for field access in pipelines**
`ItemAdapter` is used instead of direct `item["field"]` access. This is the Scrapy-recommended approach and makes pipelines forward-compatible with all item types (dict, dataclass, Scrapy Item).

**5. `BASE_DIR` with `pathlib` for all file paths**
All output paths in `settings.py` use `pathlib.Path` with `BASE_DIR` as the anchor. This ensures paths work correctly on Windows, Mac, Linux, and inside Docker — no hardcoded separators.

**6. Both CSS and XPath selectors**
CSS selectors are used where class/attribute targeting is simple (`p.price_color::text`). XPath is used where text normalization or complex conditions are needed (`normalize-space()`, `contains(@class, ...)`). This demonstrates mastery of both approaches.

**7. `overwrite: True` in FEEDS**
Without this, Scrapy appends to existing files on each run. With `overwrite: True`, each run produces a clean, deduplicated output — critical for data integrity.

**8. `bind_address = 0.0.0.0` in Scrapyd**
Scrapyd defaults to `127.0.0.1` (only accessible inside the container). Setting `0.0.0.0` allows the host machine to reach Scrapyd via the mapped Docker port.

---

## ⚠️ Known Limitations

**1. No duplicate detection in SQLite**
Running the spider multiple times inserts duplicate records into the database. A `UNIQUE` constraint on `product_url` or a pre-insert check would fix this but was intentionally omitted to keep the pipeline simple.

**2. Randomness means different results each run**
Since categories and books are randomly selected, each run produces different output. This is by design per the assignment requirements, but means results are not reproducible without seeding `random`.

**3. Output files stay inside Docker unless mounted**
If the container is run without `-v` volume mounts, exported files (`data/`, `database/`) exist only inside the container and are lost when it stops. Always use volume mounts in production.

**4. SQLite not suitable for concurrent access**
SQLite is used as required by the assignment. For a high-concurrency production system, PostgreSQL or MongoDB would be more appropriate.

**5. No retry logic for failed requests**
If a book detail page fails to load, that book is skipped silently. Scrapy's built-in retry middleware could be enabled in `settings.py` to handle transient failures.
