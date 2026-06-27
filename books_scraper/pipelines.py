# books_scraper/pipelines.py

import re
import sqlite3
from itemadapter import ItemAdapter


class DataCleaningPipeline:
    """Clean and normalize BookItem fields before storage."""

    # Fields that should be normalized to title case
    TEXT_FIELDS = ("title", "category")

    def process_item(self, item, spider):
        """Normalize item fields and return the cleaned item."""
        adapter = ItemAdapter(item)

        # Trim whitespace from all string values
        for field_name in adapter.field_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()

        # Normalize text fields to title case
        for field_name in self.TEXT_FIELDS:
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip().title()

        # Convert price text to float
        raw_price = adapter.get("price")
        if raw_price:
            cleaned_price = re.sub(r"[^\d.]", "", raw_price)
            adapter["price"] = float(cleaned_price)

        # Convert availability to boolean
        raw_availability = adapter.get("availability")
        if isinstance(raw_availability, str):
            normalized = raw_availability.strip().lower()
            adapter["availability"] = "in stock" in normalized
        else:
            adapter["availability"] = bool(raw_availability)

        spider.logger.debug(f"Cleaned item: {item['title']}")
        return item


class SQLitePipeline:
    """Persist cleaned BookItem records to a local SQLite database."""

    DB_PATH = "database/books.db"

    def open_spider(self, spider):
        """Open the SQLite DB, ensure books table exists, and clear stale data."""
        
        spider.logger.info(f"Opening SQLite connection: {self.DB_PATH}")
        self.connection = sqlite3.connect(self.DB_PATH)
        self.cursor = self.connection.cursor()
        self._create_table()
        
        # Clear previous run's data to stay in sync with exported files
        self.cursor.execute("DELETE FROM books")
        self.connection.commit()
        spider.logger.info("Cleared previous records from books table.")

    def _create_table(self):
        """Create the books table if it is not already present."""

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT    NOT NULL,
                price        REAL    NOT NULL,
                availability INTEGER NOT NULL,
                product_url  TEXT    NOT NULL,
                image_url    TEXT    NOT NULL,
                category     TEXT    NOT NULL
            )
        """
        )
        self.connection.commit()

    def process_item(self, item, spider):
        """Insert the cleaned BookItem into the SQLite books table."""
        adapter = ItemAdapter(item)

        self.cursor.execute(
            """
            INSERT INTO books (title, price, availability, product_url, image_url, category) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                adapter["title"],
                adapter["price"],
                int(bool(adapter.get("availability", False))),  # store as 0/1
                adapter["product_url"],
                adapter["image_url"],
                adapter["category"],
            ),
        )

        spider.logger.debug(f"Inserted into DB: {adapter['title']}")
        return item

    def close_spider(self, spider):
        """Commit pending inserts and close the database connection."""

        self.connection.commit()
        self.connection.close()
        spider.logger.info("SQLite connection closed. All records committed.")
