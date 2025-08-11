import asyncio
import aiohttp
import feedparser
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time  # Import time for date parsing

from manage_podcasts.config import DOWNLOADS_FOLDER

# --- Configuration ---
FEED_URL = "https://feeds.acast.com/public/shows/ftnewsbriefing"
DOWNLOAD_DIR = (
    "audio_files/ft_news_briefing_episodes"  # Changed directory name slightly
)
NUM_EPISODES = 10
DOWNLOAD_DELAY_SECONDS = 2  # Delay between download attempts


# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Helper Functions ---


def sanitize_filename(name: str) -> str:
    """Removes characters invalid for filenames and replaces spaces."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.replace(" ", "_").replace(":", "_")  # Also replace colons
    return name[:150]


def get_episode_audio_url(entry: Dict[str, Any]) -> Optional[str]:
    """Extracts the audio URL from a feedparser entry."""
    if "enclosures" in entry and entry.enclosures:
        for enclosure in entry.enclosures:
            if enclosure.get("type", "").startswith("audio/"):
                return enclosure.get("href")
    logging.warning(
        f"Could not find audio enclosure for: {entry.get('title', 'Unknown Title')}"
    )
    return None


def sort_episodes(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sorts episodes by published date, latest first."""

    def get_published_datetime(entry: Dict[str, Any]) -> datetime:
        """Safely parses published_parsed struct_time into datetime."""
        default_date = datetime.min  # Use min for sorting unknowns to the end
        if "published_parsed" in entry and entry.published_parsed:
            try:
                # feedparser returns time.struct_time, convert to datetime
                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
            except (TypeError, ValueError, OverflowError) as e:
                logging.warning(
                    f"Could not parse date for '{entry.get('title', 'Unknown')}': {e}. Using default."
                )
                return default_date
        elif "published" in entry:
            # Fallback: try parsing the string if struct_time is missing/bad
            try:
                # Attempt standard RFC formats, add more if needed
                return datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                try:
                    return datetime.strptime(
                        entry.published, "%a, %d %b %Y %H:%M:%S %Z"
                    )  # Alternative format
                except ValueError as e_str:
                    logging.warning(
                        f"Could not parse date string '{entry.published}' for '{entry.get('title', 'Unknown')}': {e_str}. Using default."
                    )
                    return default_date
        return default_date

    return sorted(entries, key=get_published_datetime, reverse=True)


# --- Core Async Functions ---


async def fetch_feed(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    """Fetches the RSS feed content asynchronously."""
    logging.info(f"Fetching feed from: {url}")
    try:
        # Add a basic User-Agent header, some servers block default agents
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with session.get(
            url, headers=headers, timeout=30
        ) as response:  # Added timeout
            response.raise_for_status()
            content = await response.text()
            logging.info("Successfully fetched feed content.")
            return content
    except asyncio.TimeoutError:
        logging.error(f"Timeout error fetching feed: {url}")
        return None
    except aiohttp.ClientError as e:
        logging.error(f"Client error fetching feed: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching feed: {e}")
        return None


async def download_episode(
    session: aiohttp.ClientSession, episode_data: Dict[str, Any], download_dir: str
) -> Tuple[str, bool]:
    """Downloads a single episode asynchronously."""
    title = episode_data.get("title", "Unknown_Episode")
    audio_url = episode_data.get("audio_url")

    if not audio_url:
        logging.warning(f"Skipping '{title}' - No audio URL found.")
        return title, False

    file_extension = os.path.splitext(audio_url)[1].lower()
    if not file_extension or not file_extension.startswith("."):
        # Check content type from URL if possible, otherwise default
        if "mp3" in audio_url.lower():
            file_extension = ".mp3"
        elif "m4a" in audio_url.lower():
            file_extension = ".m4a"
        else:
            file_extension = ".mp3"  # Default assumption

    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title}{file_extension}"
    filepath = os.path.join(download_dir, filename)

    if os.path.exists(filepath):
        logging.info(f"Skipping '{title}' - File already exists: {filename}")
        return title, True

    logging.info(f"Starting download: '{title}' -> {filename}")
    try:
        # <<< CHANGE: Try a specific podcast app User-Agent >>>
        # Example: Mimic Overcast app
        podcast_user_agent = "Overcast/2022.1 (iPhone; iOS 15.4; Build 494)"
        # Example: Mimic Apple Podcasts (CoreMedia) - Often allowed
        # podcast_user_agent = 'AppleCoreMedia/1.0.0.19E241 (iPhone; U; CPU OS 15_4 like Mac OS X; en_us)'

        headers = {
            "User-Agent": podcast_user_agent,  # Use the podcast app agent
            "Referer": FEED_URL,
            # Add other common headers apps might send? (Optional, might not help)
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'en-us'
        }
        async with session.get(
            audio_url, headers=headers, timeout=300
        ) as response:  # Longer timeout for downloads
            if response.status != 200:
                logging.error(
                    f"Download failed for '{title}': Status {response.status}"
                )
                return title, False

            os.makedirs(download_dir, exist_ok=True)

            async with aiofiles.open(filepath, mode="wb") as afp:
                downloaded_size = 0
                async for chunk in response.content.iter_chunked(8192):
                    await afp.write(chunk)
                    downloaded_size += len(chunk)
            logging.info(
                f"Finished download: '{title}' ({downloaded_size / 1024 / 1024:.2f} MB)"
            )
            return title, True
    except asyncio.TimeoutError:
        logging.error(f"Timeout error downloading '{title}': {audio_url}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return title, False
    except aiohttp.ClientError as e:
        logging.error(f"Network error downloading '{title}': {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return title, False
    except IOError as e:
        logging.error(f"File write error for '{title}': {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return title, False
    except Exception as e:
        logging.error(f"An unexpected error occurred downloading '{title}': {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return title, False


# --- Main Orchestration ---


async def main():
    """Main function to fetch feed and download episodes."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    logging.info(f"Using download directory: {DOWNLOAD_DIR}")

    async with aiohttp.ClientSession() as session:
        feed_content = await fetch_feed(session, FEED_URL)
        if not feed_content:
            logging.error("Could not fetch feed. Exiting.")
            return

        feed_data = feedparser.parse(feed_content)
        if feed_data.bozo:
            logging.warning(f"Feed may be ill-formed: {feed_data.bozo_exception}")

        if not feed_data.entries:
            logging.error("No entries found in the feed. Exiting.")
            return

        sorted_entries = sort_episodes(feed_data.entries)

        episodes_to_download = []
        for entry in sorted_entries[:NUM_EPISODES]:
            audio_url = get_episode_audio_url(entry)
            if audio_url:
                episodes_to_download.append(
                    {
                        "title": entry.get("title", "Unknown Title"),
                        "audio_url": audio_url,
                        "published_parsed": entry.get(
                            "published_parsed"
                        ),  # Keep for reference
                        "id": entry.get("id", entry.get("link", audio_url)),
                    }
                )
            else:
                logging.warning(
                    f"Could not get audio URL for: {entry.get('title', 'Unknown Title')}"
                )

        if not episodes_to_download:
            logging.warning("No episodes found with valid audio URLs among the latest.")
            return

        logging.info(
            f"Found {len(episodes_to_download)} latest episodes with audio URLs to download."
        )

        results = []
        for i, episode_data in enumerate(episodes_to_download):
            logging.info(
                f"--- Attempting episode {i+1}/{len(episodes_to_download)} ---"
            )
            result = await download_episode(session, episode_data, DOWNLOAD_DIR)
            results.append(result)
            if i < len(episodes_to_download) - 1:  # Don't sleep after the last one
                logging.info(
                    f"Waiting for {DOWNLOAD_DELAY_SECONDS} seconds before next download..."
                )
                await asyncio.sleep(DOWNLOAD_DELAY_SECONDS)

        success_count = sum(1 for _, success in results if success)
        fail_count = len(results) - success_count
        logging.info(f"--- Download Summary ---")
        logging.info(f"Successfully processed/downloaded: {success_count}")
        logging.info(f"Failed/Skipped (check logs): {fail_count}")


# if __name__ == "__main__":
#     asyncio.run(main())

url = "https://stitcher2.acast.com/livestitches/5bdeb9391f003ce7f5028d28e10cae22.mp3?aid=681536f69704d99f841b965a&chid=73fe3ede-5c5c-4850-96a8-30db8dbae8bf&ci=741a0VrrnY0dSICttCrUBzuZXhMF25I5Y0eCDYTkOyu7cCvKvVMXYw%3D%3D&pf=rss&range=bytes%3D0-&sv=sphinx%401.236.0&uid=ea86875d054c471fec8834081433659f&Expires=1746387959439&Key-Pair-Id=K38CTQXUSD0VVB&Signature=WOXxtVf1JHzIyexB9KOc0yiQ3G8ZYiscW8yk4MiFjuaz9IGwktUOYGajyC9Om4JC4On7jO-S48Qbe-3WeVxjNmq6gjzMmCX1xL-1Rp~ZdnarPB2laT-L3TYJGns3xHZjoVzlFtBg0Pb4tOikklovPcGTepHwntIpujp-LY3GsqdaSRDTYSVRfo0qrp1HyENyZHEZEv7p6-jmPhjrpi2P53sC4INmsyzcEhP08meFVc-ZIuwRNGzJy~REQwWEE1rQIWMo2yRpPN-JSvRHdraOXWbMjVg2MoGiH9i3vUr~vpZaaawXSyiQ0ZBs9Igh3Lfm32zjwedzkq4nOhLLF59zxg__"

import asyncio
import aiohttp
import aiofiles
import os

# --- Configuration ---
# <<< Replace with the actual URL of the file you want to download >>>
url_to_download = "https://www.python.org/static/img/python-logo@2x.png"  # Example URL

# <<< Replace with the desired local filename/path to save the file >>>
local_filename = "downloaded_file_async.png"
chunk_size = 8192  # Define chunk size for downloading (8KB)


# --- Async Download Function ---
async def download_file_async(url: str, filename: str):
    """Downloads a file asynchronously using streaming."""
    print(f"Attempting to download file from: {url}")
    print(f"Saving to: {filename}")
    try:
        # Create an async HTTP session
        async with aiohttp.ClientSession() as session:
            # Start the async GET request
            async with session.get(url) as response:
                # Check if the request was successful (status code 200 OK)
                response.raise_for_status()  # Raises ClientResponseError for bad responses

                # Open the local file asynchronously in binary write mode
                async with aiofiles.open(filename, mode="wb") as afp:
                    # Iterate over chunks asynchronously and write them
                    downloaded_size = 0
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await afp.write(chunk)
                        downloaded_size += len(chunk)
                    print(f"Downloaded {downloaded_size / 1024:.2f} KB")

        print(f"Successfully downloaded '{filename}'")
        return True  # Indicate success

    # --- Combined Exception Handling ---
    except (aiohttp.ClientError, IOError, Exception) as e:
        # Handles aiohttp client errors (network, bad status),
        # IOError (file writing errors), and any other unexpected exceptions.
        print(f"Error during download or file writing: {e}")
        # Attempt to remove partially downloaded file
        if os.path.exists(filename):
            try:
                # In async, direct os.remove might block, but for cleanup it's often acceptable.
                # For truly non-blocking delete, use aiofiles.os.remove (requires newer aiofiles)
                # or run os.remove in an executor. Keeping it simple here.
                os.remove(filename)
                print(f"Removed potentially incomplete file: {filename}")
            except OSError as rm_e:
                print(f"Error removing partial file {filename}: {rm_e}")
        return False  # Indicate failure


# --- Main execution ---
# async def download_file(title, url):
async def download_file():

    # title = "Swamp_Notes__The_conservative_view_on_tariffs_now"
    #
    url = "https://d1bxy2pveef3fq.cloudfront.net/episodes/original/51208493?session_id=fbf90ed9-f2f4-573c-8952-7767ebe8a94a&ab=256&al=924242&ao=1024&cc=NYNNNNYYYY&ct=DOWNLOAD&episode_id=67295852&show_id=4252013&user_id=12087503&organization_id=8727572&tenant=SPREAKER&timestamp=1754860884&ppi=555acab4-1f31-573f-af7d-db18d849040f&epi=9e0af943-078c-5518-b764-f7b3d813061b&media_type=static&Expires=1754947284&Key-Pair-Id=K1J2BR3INU6RYD&Signature=iSSPbMp58IrX5zbxvLRVuRlDsjTWB-GFVvZHTVUN3CUhWEEIrcOaAjD8kkBg9efEEjR5TOQGr4cEzM805HwVwFfiOhWEcBKAgQOyagD6XRNBM3k6SnrovhsyUoESUCJKNcw5wHDaSibYRPyEi2Lrl3j31HFjLL~RN73uGOQ7O-nQ7Z1-w6hDa8RDpna1z0UyMe4CnDiav~sQQlNysUYlBUUOHgj8f~5j9cZN57dkhl1tQXAREb0eahST-UYn6qG~CRKkaKpVnANohIKaoNaghy4MMIrEPuKh3Y6s7Fjno02o3~Z-~AwNRWjEke1J3G6hsfVdWvKRZL5zfk9W8VSE4A__"
    #
    # path = (
    #     "C:\\dev\\podsights\\manage_podcasts\\audio_files\\ft_news_briefing_episodes\\"
    # )

    sanitized_title = sanitize_filename("agnews test")

    fs_location = DOWNLOADS_FOLDER + sanitized_title + ".mp3"

    await download_file_async(url, fs_location)

    return fs_location


if __name__ == "__main__":
    # On Windows, the default event loop policy might need changing for aiohttp + aiofiles
    # Uncomment the following lines if you encounter runtime errors related to event loops on Windows:
    # if os.name == 'nt':
    #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the main async function
    # asyncio.run(main())
    asyncio.run(download_file())
