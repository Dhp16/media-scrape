import asyncio

from db.engine import start_db_engine

from manage_podcasts.my_types import Media
from manage_podcasts.utils.naming import sanitize_title
from manage_podcasts.audio_files.download_with_browser import download_file
from manage_podcasts.transcription import transcribe
from manage_podcasts.nlp import find_org_counts

MODES = {0: "Named entity recognition frequency", 1: "Keyword slack alert"}

MODE = 1


if __name__ == "__main__":
    if MODE == 0:
        print("Running async setup...")
        asyncio.run(start_db_engine())
        print("Finished async setup...")

        url = "https://audio.listennotes.com/e/p/101487a649e44730b02a0833a89e6533/?_gl=1*4bypoe*_gcl_au*NDA0NzM5MC4xNzQ2MzgwMzI5*_ga*ODYxOTIwODYyLjE3NDYzODA1OTY.*_ga_T0PZE2Z7L4*czE3NDY1NjIwNzgkbzIkZzEkdDE3NDY1NjM4MTAkajU5JGwwJGgw"
        podcast_series_downloads_folder = "C:\\dev\\podsights\\manage_podcasts\\audio_files\\ft_news_briefing_episodes\\"
        episode_name = "The Catholic Church after Pope Francis"
        sanitized_episode_name = sanitize_title(episode_name)

        downloaded_audio_file_path = download_file(
            url, podcast_series_downloads_folder, sanitized_episode_name
        )

        transcription = transcribe(downloaded_audio_file_path)

        org_counts = find_org_counts(transcription)

    if MODE == 1:
        print("Starting keyword search")
        temp_downloads_folder = (
            "C:\\dev\\podsights\\manage_podcasts\\audio_files\\temp\\"
        )

        keywords = {
            "Weather & Growing Conditions": [
                "drought",
                "dry spell",
                "lack of rain",
                "below-average rainfall",
                "water stress",
                "moisture deficit",
                "parched",
                "water restrictions",
                "low river levels",
                "flood",
                "flooding",
                "deluge",
                "waterlogged",
                "inundated",
                "record rainfall",
                "hailstorm",
                "hail damage",
                "soil erosion",
                "frost",
                "freeze",
                "cold snap",
                "unseasonal cold",
                "heatwave",
                "record heat",
                "extreme temperatures",
                "scorching",
                "crop stress",
                "poor conditions",
                "yield estimates cut",
                "yield forecast lowered",
                "stunted growth",
                "delayed planting",
                "delayed harvest",
            ],
            "Pests & Disease": [
                "disease outbreak",
                "pest infestation",
                "locust swarm",
                "fungus",
                "blight",
                "rust",
                "culling",
                "quarantine",
                "movement restrictions",
                "biosecurity",
                "African Swine Fever",
                "Avian Influenza",
                "Foot and Mouth",
            ],
            "Logistics & Supply Chain": [
                "port congestion",
                "port strike",
                "vessel lineup",
                "loading delays",
                "port closure",
                "union action",
                "trucker strike",
                "rail strike",
                "rail disruption",
                "road blockade",
                "bridge collapse",
                "low water levels",
                "plant shutdown",
                "factory fire",
                "maintenance",
                "reduced capacity",
                "crush margins",
                "milling issues",
            ],
            "Government Policy & Geopolitics": [
                "export ban",
                "export tax",
                "export quota",
                "import tariff",
                "trade deal",
                "trade dispute",
                "subsidy",
                "new regulations",
                "biofuel mandate",
                "acreage report",
                "planting intentions",
                "strategic reserve",
                "price controls",
                "unrest",
                "protests",
                "sanctions",
                "border closure",
                "conflict",
            ],
            "Economic & Demand Signals": [
                "demand destruction",
                "slowing demand",
                "record exports",
                "strong demand",
                "animal feed demand",
                "herd expansion",
                "herd liquidation",
                "improving margins",
            ],
        }

        sources = {
            {
                "type": Media.PODCAST,
                "name": "Agrolink",
                "url": "https://www.listennotes.com/podcasts/agrolink-news-agrolink-vcfmUpiP2zO/",
                "language": "portugese",
                "language_code": "pt",
                "latest_episode": {},
            },
        }

        # handle_podcasts(podcasts, keywords)
