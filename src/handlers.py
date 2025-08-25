import asyncio
import itertools
import os
import re

from flashtext import KeywordProcessor

from config import TIMOUT_MS, DOWNLOADS_FOLDER
from src.my_types import Media
from src.selenium_handler import download_audio
from src.download_series import fetch_and_extract_latest_episode
from src.transcription import transcribe
from src.slack_alert import send_slack_message


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

    def find_words(sentence):
        nonlocal keyword_processor
        return keyword_processor.extract_keywords(sentence)

    sentences = re.split(r"(?<=[.?!])\s+", text)

    keywords_with_context = {}
    for sentence in sentences:
        found_in_sentence = find_words(sentence)
        for keyword in found_in_sentence:
            # TODO: handle multiple appearances
            if keyword in keywords_with_context:
                continue

            keywords_with_context[keyword] = sentence.strip()

    return keywords_with_context


def format_slack_message(source, episode, keywords_with_context):
    message_parts = []
    header = f"{len(keywords_with_context)} keywords found in latest episode of *{source['name']}* titled: *{episode['title']}* published at {episode['published_at']}:"
    message_parts.append(header)

    for keyword, sentence in keywords_with_context.items():
        bold_sentence = sentence.replace(keyword, f"*{keyword}*")

        # Format the bullet point line using Slack's mrkdwn
        line = f"• *{keyword}*: {bold_sentence}"
        message_parts.append(line)

    message_parts.append(f"The episode can be found here: {episode['link']}")

    return "\n".join(message_parts)


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
    keywords_with_context = find_keywords(transcription["text"], keywords)

    if not keywords_with_context:
        print(
            f"No keywords found in latest episode of {source['name']} titled: {latest_episode["title"]}."
        )
        return

    print("Step 5: Send slack alert...")

    alert_message = format_slack_message(source, latest_episode, keywords_with_context)
    send_slack_message(alert_message)

    return latest_episode


async def iterate_through_media(sources, keywords):
    while True:
        for source in sources:
            if source["type"] == Media.PODCAST:
                source["latest_episode"] = await handle_podcast(source, keywords)

        print(
            f"\nFinished cycling through sources, waiting {TIMOUT_MS/(60*1000)} minutes..."
        )

        clean_up_temp_directory()
        await asyncio.sleep(TIMOUT_MS)


def scrape_sources_for_alerts(sources, keywords):
    keywords_flat = list(itertools.chain.from_iterable(keywords.values()))
    asyncio.run(iterate_through_media(sources, keywords_flat))


if __name__ == "__main__":
    msg = format_slack_message(
        {"name": "Agrinews"},
        {
            "title": "Agrinews 11th of July",
            "link": "https://www.listennotes.com/podcasts/agrolink-news-agrolink-vcfmUpiP2zO/",
        },
        {
            "export": "Record export tariffs applied",
            "text": "Everywhere you can imagine there is text.",
        },
    )
    send_slack_message(msg)
