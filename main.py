import asyncio

from config import KEYWORDS, SOURCES

from src.handlers import scrape_sources_for_alerts
from src.harvestor import harvest
from src.my_types import Mode

RUN_MODE = Mode.HARVEST

if __name__ == "__main__":
    if RUN_MODE == Mode.ALERT:
        scrape_sources_for_alerts(SOURCES, KEYWORDS)
    elif RUN_MODE == Mode.HARVEST:
        asyncio.run(harvest())
