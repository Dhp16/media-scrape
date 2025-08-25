from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base

# The Base which all models will inherit from
Base = declarative_base()


class PodcastEpisode(Base):
    """
    Represents a single podcast episode with its compressed transcription.
    """
    __tablename__ = 'podcast_episode'

    id = Column(Integer, primary_key=True)
    podcast_name = Column(String(255), nullable=False, index=True)
    episode_title = Column(String(512), nullable=False)
    published_date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Use LargeBinary to store the compressed transcription bytes.
    # This is the database-agnostic way to handle BLOB/BYTEA types.
    compressed_transcription = Column(LargeBinary, nullable=False)

    word_count = Column(Integer, nullable=False)

    # A helper property to make the object easier to read when printed
    def __repr__(self):
        return f"<PodcastEpisode(id={self.id}, title='{self.episode_title}')>"
