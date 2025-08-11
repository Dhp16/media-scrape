import asyncio
import itertools

from manage_podcasts.download import download_file
from manage_podcasts.utils.download_series import fetch_and_extract_all_episodes
from manage_podcasts.transcription import transcribe


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
    latest_episode = fetch_and_extract_all_episodes(source["url"], latest_only=True)[0]

    if (
        source["latest_episode"]
        and latest_episode["title"] == source["latest_episode"]["title"]
    ):  # add time check
        print(f"Latest episode of {source['name']} already parsed.")
        return  # latest episode already

    # await download_file(latest_episode["title"], latest_episode["link"])
    # file_location = await download_file()
    file_location = "C:\dev\podsights\manage_podcasts\audio_files\temp\agnews_test.mp3"

    print(f"language code: {source["language_code"]} ")

    transcription = transcribe(
        file_location, source["language_code"]
    )  # also takes care of translation

    keywords_found = find_keywords(transcription, keywords)

    # handle the keywords found


def scrape_sources(sources, keywords):
    keys = list(itertools.chain.from_iterable(keywords.values()))

    source = sources[0]

    asyncio.run(handle_podcast(source, keywords))
