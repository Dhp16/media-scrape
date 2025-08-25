import zlib
import datetime

from src.db.database import async_session_factory
from src.db.models.podcast_episode import PodcastEpisode

async def save_episode(
    podcast_name: str,
    episode_title: str,
    published_date: datetime.datetime,
    transcription: str
) -> PodcastEpisode:
    """
    Compresses and saves a new podcast episode to the database asynchronously.
    """
    print(f"Compressing and saving episode: '{episode_title}'...")
    word_count = len(transcription.split())
    compressed_bytes = zlib.compress(transcription.encode('utf-8'))

    new_episode = PodcastEpisode(
        podcast_name=podcast_name,
        episode_title=episode_title,
        published_date=published_date,
        compressed_transcription=compressed_bytes,
        word_count=word_count
    )

    # Use 'async with' to get a session from the factory
    async with async_session_factory() as session:
        session.add(new_episode)
        await session.commit()
        await session.refresh(new_episode) # Refresh to get the ID from the DB

    print(f"Successfully saved episode with ID: {new_episode.id}")
    return new_episode