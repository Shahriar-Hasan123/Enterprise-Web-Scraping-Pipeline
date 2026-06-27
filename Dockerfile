# Dockerfile

# ── Base image ──────────────────────────────────────────────────────────────
# Use official Python slim image — smaller size, production ready
FROM python:3.12-slim

# ── Metadata ────────────────────────────────────────────────────────────────
LABEL maintainer="books-scraper"
LABEL description="Scrapy books scraper with Scrapyd deployment"

# ── Environment variables ────────────────────────────────────────────────────
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr — logs appear immediately
ENV PYTHONUNBUFFERED=1

# ── Set working directory ────────────────────────────────────────────────────
WORKDIR /app

# ── Install system dependencies ──────────────────────────────────────────────
# libxml2-dev and libxslt-dev are required by Scrapy's lxml parser
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Install Python dependencies ──────────────────────────────────────────────
# Copy requirements first (Docker layer caching — only re-runs if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ───────────────────────────────────────────────────────
COPY . .

# ── Create required directories ──────────────────────────────────────────────
# These are needed by Scrapyd and our spider at runtime
RUN mkdir -p eggs logs dbs data database

# ── Copy Scrapyd config ──────────────────────────────────────────────────────
# Scrapyd reads config from /etc/scrapyd/ or project root
COPY scrapyd.conf /etc/scrapyd/scrapyd.conf

# ── Expose Scrapyd port ──────────────────────────────────────────────────────
EXPOSE 6800

# ── Start Scrapyd ────────────────────────────────────────────────────────────
CMD ["scrapyd"]