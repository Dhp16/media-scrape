import os

POSTGRES_DB = os.environ.get("POSTGRES_DB", "podsights")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "router")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "localsecret")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
