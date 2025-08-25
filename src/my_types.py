from enum import StrEnum, Enum, auto

class Mode(StrEnum):
    ALERT = auto()
    HARVEST = auto()

class Media(Enum):
    """
    An Enum for common HTTP methods.
    """

    PODCAST = "PODCAST"
    NEWS_SITE = "NEWS_SITE"

