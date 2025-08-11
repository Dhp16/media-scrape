from manage_podcasts.src.handlers import scrape_sources
from manage_podcasts.config import KEYWORDS, SOURCES

if __name__ == "__main__":
    scrape_sources(SOURCES, KEYWORDS)
