import asyncio
import itertools
import os

from flashtext import KeywordProcessor

from manage_podcasts.config import TIMOUT_MS, DOWNLOADS_FOLDER
from manage_podcasts.src.my_types import Media
from manage_podcasts.src.selenium_handler import download_audio
from manage_podcasts.src.download_series import fetch_and_extract_latest_episode
from manage_podcasts.src.transcription import transcribe
from manage_podcasts.src.slack_alert import send_slack_message


def clean_up_temp_directory():
    for filename in os.listdir(DOWNLOADS_FOLDER):
        file_path = os.path.join(DOWNLOADS_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete file: {file_path} with error: {e}")


def find_keywords(text, keywords):
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list(keywords)

    return keyword_processor.extract_keywords(text)


async def handle_podcast(source, keywords):
    """
    Example source
    {
        "type": Media.PODCAST,
        "name": "Agrolink",
        "url": "https://www.listennotes.com/podcasts/agrolink-news-agrolink-vcfmUpiP2zO/",
        "language": "portugese",
        "language_code": "pt",
        "latest_episode": {},
    }
    Keywords is just a list of key words to search for
    """

    print(f"\nStep 1: Get link for latest episode of {source['name']}...")
    latest_episode = fetch_and_extract_latest_episode(source["url"])

    if (
        source.get("latest_episode", None)
        and latest_episode["title"] == source["latest_episode"]["title"]
    ):  # TODO: add time check
        print(f"Latest episode of {source['name']} already parsed.")
        return  # latest episode already

    print("Step 2: Download audio file...")

    file_location = download_audio(latest_episode["title"], latest_episode["audio_url"])

    if not file_location:
        print(
            f"Failed to download audio for latest episode of {source['name']} titled: {latest_episode["title"]}."
        )
        return

    print("Step 3: Transcribe and translate if necessary...")

    transcription = transcribe(
        file_location, source["language_code"]
    )  # returns dict with keys: ['text', 'segments', 'language']

    print("Step 4: Find keywords...")
    keywords_found = find_keywords(transcription["text"], keywords)

    if not keywords_found:
        print(
            f"No keywords found in latest episode of {source['name']} titled: {latest_episode["title"]}."
        )
        return

    print("Step 5: Send slack alert...")
    message = f"""
        Found keyword(s): {",".join(keywords_found)} in latest episode of {source['name']} titled: {latest_episode["title"]}. It can be found here: {latest_episode["link"]}.
        
        The full transcription can be found below:
        {transcription["text"]}
    """

    send_slack_message(message)
    return latest_episode


async def handle_news(source, keywords):
    pass


async def iterate_through_media(sources, keywords):
    while True:
        for source in sources:
            if source["type"] == Media.PODCAST:
                source["latest_episode"] = await handle_podcast(source, keywords)
            elif source["type"] == Media.NEWS_SITE:
                source["latest_episode"] = await handle_news(source, keywords)

        print(
            f"\nFinished cycling through sources, waiting {TIMOUT_MS/(60*1000)} minutes..."
        )

        clean_up_temp_directory()
        await asyncio.sleep(TIMOUT_MS)


def scrape_sources(sources, keywords):
    keywords_flat = list(itertools.chain.from_iterable(keywords.values()))
    asyncio.run(iterate_through_media(sources, keywords_flat))
