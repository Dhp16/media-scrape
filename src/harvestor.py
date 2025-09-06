import asyncio
import os
import sys

from datetime import datetime, timezone

from src.download_series import fetch_and_extract_latest_episode
from src.db.podcast_episode_crud import save_episode_optimized
from src.web.selenium_handler import download_audio
from src.transcription import transcribe
from src.sourcing.process_jre_xml import get_podcast_data
from src.utils.file_management import sanitize_filename


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure that a datetime is timezone-aware (UTC).
    If it's naive, assume it's UTC and set tzinfo accordingly.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        # Naive datetime → make it aware in UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def harvest():
    # series_name = "The Joe Rogan Experience"
    # url = "https://www.listennotes.com/podcasts/the-joe-rogan-experience-joe-rogan-s_ML5QqPi0v/"

    series_name = "FT News Briefing"
    url = "https://www.listennotes.com/podcasts/ft-news-briefing-financial-times-n6t_bq7QXWd/"

    language_code = "en"

    latest_episode = fetch_and_extract_latest_episode(
        url
    )  # returns {title, link, published_at}
    file_location = download_audio(latest_episode["title"], latest_episode["audio_url"])

    transcription = transcribe(
        file_location, language_code
    )  # returns dict with keys: ['text', 'segments', 'language']

    print("transcription", len(transcription), sys.getsizeof(transcription))

    try:
        published_date_obj = datetime.fromisoformat(latest_episode["published_at"])
        print(f"Parsed date: {published_date_obj}")
    except ValueError as e:
        print(f"Error parsing date: {e}. Please check the date format.")
        return

    episode = await save_episode(
        podcast_name=series_name,
        episode_title=latest_episode["title"],
        published_date=published_date_obj,
        transcription=transcription["text"],
    )

    return


async def iterate_through_jre():
    data = await get_podcast_data("sources/jre_archive.xml")

    series_name = "The Joe Rogan Experience"
    language_code = "en"

    for episode in data:
        file_location = download_audio(episode["title"], episode["audio_url"])
        transcription = transcribe(
            file_location, language_code, show_progress_bar=True
        )  # returns dict with keys: ['text', 'segments', 'language']

        episode = await save_episode_optimized(
            podcast_title=series_name,
            episode_title=episode["title"],
            published_date=ensure_utc(episode["published_at"]),
            transcription=transcription["text"],
        )

    return


if __name__ == "__main__":
    # harvest()
    asyncio.run(iterate_through_jre())
