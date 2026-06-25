import scrapy


class BookItem(scrapy.Item):
    """
    Represents a single book scraped from books.toscrape.com.

    Fields:
        title        (str)  : Book title
        price        (float): Book price as a number (currency symbol removed)
        availability (bool) : True if in stock, False otherwise
        product_url  (str)  : Full URL to the book's detail page
        image_url    (str)  : Full URL to the book's cover image
        category     (str)  : Category the book belongs to
    """

    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
