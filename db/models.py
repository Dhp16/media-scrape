from datetime import datetime
from typing import List, Optional

from engine import Base

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class PodcastSeries(Base):
    __tablename__ = "podcast_series"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relationships (One-to-Many)
    episodes: Mapped[List["PodcastEpisode"]] = relationship(
        back_populates="series", cascade="all, delete-orphan"
    )


    def __repr__(self) -> str:
        return f"<PodcastSeries id={self.id} name='{self.name}'>"


class PodcastEpisode(Base):
    __tablename__ = "podcast_episodes"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parsed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    series_id: Mapped[int] = mapped_column(ForeignKey("podcast_series.id"), nullable=False)
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now() # Let DB handle timestamp
    )

    # Relationships (Many-to-One)
    series: Mapped["PodcastSeries"] = relationship(back_populates="episodes")

    def __repr__(self) -> str:
        return f"<PodcastEpisode id={self.id} name='{self.name}' series_id={self.series_id}>"
