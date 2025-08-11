import asyncio
import itertools

from flashtext import KeywordProcessor

from manage_podcasts.selenium_handler import download_audio_from_redirect
from manage_podcasts.utils.download_series import fetch_and_extract_all_episodes
from manage_podcasts.transcription import transcribe
from manage_podcasts.slack_alert import send_slack_message


def find_keywords(text, keywords):
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list(keywords)

    found_keywords = keyword_processor.extract_keywords(text)

    print("Found keywords:")
    print(found_keywords)
    return found_keywords


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

    # Step 1: Get link for latest episode
    latest_episode = fetch_and_extract_all_episodes(source["url"], latest_only=True)[0]

    if (
        source["latest_episode"]
        and latest_episode["title"] == source["latest_episode"]["title"]
    ):  # TODO: add time check
        print(f"Latest episode of {source['name']} already parsed.")
        return  # latest episode already

    # Step 2: Download audio file
    file_location = await download_audio_from_redirect(
        latest_episode["title"], latest_episode["audio_url"]
    )

    if not file_location:
        print(
            f"Failed to download audio for latest episode of {source['name']} titled: {latest_episode["title"]}."
        )
        return

    # Step 3: Transcribe and translate if necessary

    transcription = transcribe(
        file_location, source["language_code"]
    )  # returns dict with keys: ['text', 'segments', 'language']

    # Step 4: Find keywords
    keywords_found = find_keywords(transcription["text"], keywords)

    if not keywords_found:
        print(
            f"No keywords found in latest episode of {source['name']} titled: {latest_episode["title"]}."
        )
        return

    # Step 5: Send slack alert
    message = f"""
        Found keyword(s): {",".join(keywords_found)} in latest episode of {source['name']} titled: {latest_episode["title"]}. It can be found here: {latest_episode["link"]}.
        
        The full transcription can be found below:
        {transcription["text"]}
    """

    send_slack_message(message)


def scrape_sources(sources, keywords):
    keywords_flat = list(itertools.chain.from_iterable(keywords.values()))

    source = sources[0]

    asyncio.run(handle_podcast(source, keywords_flat))
