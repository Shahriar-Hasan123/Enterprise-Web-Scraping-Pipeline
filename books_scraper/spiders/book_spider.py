import random
import scrapy
from books_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    """Spider for books.toscrape.com - selects random categories and books, yields `BookItem`."""

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    # Constants
    CATEGORIES_TO_SELECT = 5
    BOOKS_PER_CATEGORY = 5

    def parse(self, response):
        """Extract category links from the homepage and schedule category parsing."""

        self.logger.info("Parsing homepage to discover categories...")

        all_category_links = response.css("ul.nav.nav-list li ul li a")

        # Build a list of (name, absolute_url) tuples
        categories = []
        for link in all_category_links:
            name = link.xpath("normalize-space(text())").get()  # Extracts and strips the category name text
            url = link.css("::attr(href)").get()  # Extracts the href attribute
            absolute_url = response.urljoin(url)
            categories.append((name, absolute_url))

        self.logger.info(f"Total categories discovered: {len(categories)}")

        # Randomly select 5 categories
        selected_count = min(len(categories), self.CATEGORIES_TO_SELECT)
        selected_categories = random.sample(categories, selected_count)

        self.logger.info(f"Randomly selected categories: {[category[0] for category in selected_categories]}")

        for category_name, category_url in selected_categories:
            yield response.follow(
                url=category_url,
                callback=self.parse_category,
                meta={"category_name": category_name, "book_urls": []},
            )

    def parse_category(self, response):
        """Collect book URLs for a category (uses `response.meta`). Follows pagination and yields requests for selected books."""

        category_name = response.meta["category_name"]
        book_urls = response.meta.get("book_urls", [])

        self.logger.info(f"Collecting books from category: {category_name} | URL: {response.url}")

        # Gets href from every book link on this page
        page_book_links = response.xpath("//article[@class='product_pod']//h3/a/@href").getall()

        for href in page_book_links:
            absolute_url = response.urljoin(href)
            book_urls.append(absolute_url)

        # Check if a "next" pagination button exists
        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            next_url = response.urljoin(next_page)
            self.logger.info(f"Following next page: {next_url}")
            yield response.follow(
                url=next_url,
                callback=self.parse_category,
                meta={
                    "category_name": category_name,
                    "book_urls": book_urls,
                },
            )
        else:
            # No more pages - now randomly select 5 books
            self.logger.info(
                f"Category '{category_name}' has {len(book_urls)} books total. "
                f"Selecting {self.BOOKS_PER_CATEGORY} randomly."
            )

            selected_books = random.sample(book_urls, min(self.BOOKS_PER_CATEGORY, len(book_urls)))

            for book_url in selected_books:
                yield response.follow(
                    url=book_url,
                    callback=self.parse_book,
                    meta={"category_name": category_name},
                )

    def parse_book(self, response):
        """Parse a book detail page and extract all required fields."""

        category_name = response.meta.get("category_name")
        self.logger.info(f"Scraping book: {response.url}")

        item = BookItem()
        item["title"] = response.xpath("//h1/text()").get()
        item["price"] = response.css("p.price_color::text").get()
        item["availability"] = response.xpath("normalize-space(//p[contains(@class, 'availability')])").get()

        relative_image = response.css("img.thumbnail::attr(src)").get()
        item["image_url"] = response.urljoin(relative_image)
        item["product_url"] = response.url
        item["category"] = category_name

        yield item
