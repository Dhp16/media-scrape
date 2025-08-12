import os

from manage_podcasts.src.my_types import Media

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "C09A8LUMU4R")

SOURCES = [
    {
        "type": Media.PODCAST,
        "name": "Agrolink",  # Brazilian agricultural news
        "url": "https://www.listennotes.com/podcasts/agrolink-news-agrolink-vcfmUpiP2zO/",
        "language": "portuguese",
        "language_code": "pt",
    },
    {
        "type": Media.PODCAST,
        "name": "Agriculture Today",
        "url": "https://www.listennotes.com/podcasts/agriculture-today-kansas-state-university-2V9_Cbx0GAm/",
        "language": "english",
        "language_code": "en",
    },
    {
        "type": Media.PODCAST,
        "name": "Canal Rural Clima",  # Brazilian weather
        "url": "https://www.listennotes.com/podcasts/canal-rural-clima-pod360-canal-rural-rox3XgWqy0s/",
        "language": "portuguese",
        "language_code": "pt",
    },
]


KEYWORDS = {
    "Weather & Growing Conditions": [
        "drought",
        "dry spell",
        "lack of rain",
        "below-average rainfall",
        "water stress",
        "moisture deficit",
        "parched",
        "water restrictions",
        "low river levels",
        "flood",
        "flooding",
        "deluge",
        "waterlogged",
        "inundated",
        "record rainfall",
        "hailstorm",
        "hail damage",
        "soil erosion",
        "frost",
        "freeze",
        "cold snap",
        "unseasonal cold",
        "heatwave",
        "record heat",
        "extreme temperatures",
        "scorching",
        "crop stress",
        "poor conditions",
        "yield estimates cut",
        "yield forecast lowered",
        "stunted growth",
        "delayed planting",
        "delayed harvest",
    ],
    "Pests & Disease": [
        "disease outbreak",
        "pest infestation",
        "locust swarm",
        "fungus",
        "blight",
        "rust",
        "culling",
        "quarantine",
        "movement restrictions",
        "biosecurity",
        "African Swine Fever",
        "Avian Influenza",
        "Foot and Mouth",
    ],
    "Logistics & Supply Chain": [
        "port congestion",
        "port strike",
        "vessel lineup",
        "loading delays",
        "port closure",
        "union action",
        "trucker strike",
        "rail strike",
        "rail disruption",
        "road blockade",
        "bridge collapse",
        "low water levels",
        "plant shutdown",
        "factory fire",
        "maintenance",
        "reduced capacity",
        "crush margins",
        "milling issues",
    ],
    "Government Policy & Geopolitics": [
        "export ban",
        "export tax",
        "export quota",
        "import tariff",
        "trade deal",
        "trade dispute",
        "subsidy",
        "new regulations",
        "biofuel mandate",
        "acreage report",
        "planting intentions",
        "strategic reserve",
        "price controls",
        "unrest",
        "protests",
        "sanctions",
        "border closure",
        "conflict",
    ],
    "Economic & Demand Signals": [
        "demand destruction",
        "slowing demand",
        "record exports",
        "strong demand",
        "animal feed demand",
        "herd expansion",
        "herd liquidation",
        "improving margins",
    ],
}

TIMOUT_MS = 15 * 60 * 1000  # time between checks for updates

DOWNLOADS_FOLDER = "temp\\"  # where audio and text files are stored for processing
