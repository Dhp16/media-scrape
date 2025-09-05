import zlib
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, func

from src.db.database import async_session_factory
from src.db.models.podcast_episode import PodcastEpisode


async def save_episode_optimized(
    podcast_name: str,
    episode_title: str,
    published_date: datetime.datetime,
    transcription: str,
    async_session: AsyncSession,  # Pass the session in for better transaction control
) -> PodcastEpisode:
    """
    Compresses a transcript, generates a search vector, and saves a new
    podcast episode to the database in a single, efficient transaction.
    """
    print(f"Compressing and preparing episode: '{episode_title}'...")
    word_count = len(transcription.split())

    # Compress the raw text for efficient storage
    compressed_bytes = zlib.compress(transcription.encode("utf-8"))

    # We will no longer use session.add(). Instead, we build an INSERT statement
    # that uses PostgreSQL's to_tsvector function on the fly. This is far more
    # efficient as the raw text is sent to the DB once and never stored.

    stmt = (
        insert(PodcastEpisode)
        .values(
            podcast_name=podcast_name,
            episode_title=episode_title,
            published_date=published_date,
            compressed_transcription=compressed_bytes,
            word_count=word_count,
            # This is the key part: we call the DB function directly.
            # 'english' is the dictionary to use for stemming and stop words.
            search_vector=func.to_tsvector("english", transcription),
        )
        .returning(PodcastEpisode)  # Ask the DB to return the newly created row
    )

    result = await async_session.execute(stmt)
    await async_session.commit()

    new_episode = result.scalar_one()  # Get the single ORM object back

    print(f"Successfully saved episode with ID: {new_episode.id}")
    return new_episode
