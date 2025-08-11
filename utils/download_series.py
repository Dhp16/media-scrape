import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os


def parse_single_episode_item(item_div, base_url):
    """
    Helper function to parse a single episode item div (common structure).
    Args:
        item_div (BeautifulSoup.Tag): The div tag containing one episode's details.
        base_url (str): The base URL for resolving relative links.
    Returns:
        dict: A dictionary with 'title' and 'link' or None if not found.
    """
    # Find the h3 tag which contains the link and title
    # The h3 has classes like "text-black text-base font-semibold w-full mb-2"
    h3_tag = item_div.find(
        "h3", class_=lambda c: c and "font-semibold" in c and "mb-2" in c
    )
    if not h3_tag:
        return None

    link_tag = h3_tag.find(
        "a",
        href=True,
        class_=lambda c: c and "line-clamp-2" in c and "ln-wrap-line" in c,
    )
    if not link_tag:
        return None

    time_tag = item_div.find("time", attrs={"datetime": True})
    published_at = time_tag.get("datetime") if time_tag else None

    title = link_tag.get_text(strip=True)
    episode_link_href = link_tag.get("href")

    if title and episode_link_href:
        absolute_link = urljoin(base_url, episode_link_href)
        return {"title": title, "link": absolute_link, "published_at": published_at}
    return None


def parse_latest_episode_from_html(soup, base_url):
    """
    Parses the "LATEST EPISODE" section from the provided BeautifulSoup object.
    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the full page.
        base_url (str): The base URL for resolving relative links.
    Returns:
        dict: A dictionary with 'title' and 'link' for the latest episode, or None.
    """
    print("Attempting to parse LATEST EPISODE section...")
    latest_episode_heading = None
    # The <h2> has class "ln-page-card-title" and contains "LATEST EPISODE"
    for h2_tag in soup.find_all("h2", class_="ln-page-card-title"):
        if "LATEST EPISODE" in h2_tag.get_text(strip=True):
            latest_episode_heading = h2_tag
            break

    if not latest_episode_heading:
        print("Could not find the 'LATEST EPISODE' heading.")
        return None

    # The "LATEST EPISODE" is within a <div class="ln-page-card">
    main_card_div = latest_episode_heading.find_parent("div", class_="ln-page-card")
    if not main_card_div:
        print("Could not find the parent 'ln-page-card' for 'LATEST EPISODE'.")
        return None

    # The episode details are usually within a structure like:
    # <div class="grid grid-cols-1 gap-4"> (directly under main_card_div or one level down)
    #   <div class="flex"> ... this is the item div we need for parse_single_episode_item

    # Let's find the first div that looks like an episode item container
    # In the provided snippet, the episode item itself is NOT <div class="pt-4">
    # but rather the <div class="grid grid-cols-1 gap-4"> contains the <div class="flex">

    # The episode item structure is directly within the main_card_div,
    # often starting with a <div class="grid grid-cols-1 gap-4">
    # then <div class="flex"> which contains the actual episode details.

    episode_item_container = main_card_div.find(
        "div",
        class_=lambda c: c and "grid" in c and "grid-cols-1" in c and "gap-4" in c,
    )
    if not episode_item_container:
        print(
            "Could not find episode item container (div with grid classes) in LATEST section."
        )
        return None

    # The actual episode content is often in a <div class="flex"> within this grid.
    # We are looking for the first such item.
    episode_item_div = episode_item_container.find(
        "div", class_="flex"
    )  # This is the div containing the h3
    if not episode_item_div:
        print("Could not find the 'div.flex' for the latest episode item.")
        return None

    return parse_single_episode_item(episode_item_div, base_url)


def parse_previous_episodes_from_html(soup, base_url):
    """
    Parses the "PREVIOUS EPISODES" section from the provided BeautifulSoup object.
    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the full page.
        base_url (str): The base URL for resolving relative links.
    Returns:
        list: A list of dictionaries, each with 'title' and 'link'.
    """
    print("Attempting to parse PREVIOUS EPISODES section...")
    episodes_data = []

    previous_episodes_heading = None
    for h2_tag in soup.find_all(
        "h2", class_="flex-1 truncate"
    ):  # Class for previous episodes heading
        if "PREVIOUS EPISODES" in h2_tag.get_text(strip=True):
            previous_episodes_heading = h2_tag
            break

    if not previous_episodes_heading:
        print("Could not find the 'PREVIOUS EPISODES' heading.")
        return episodes_data

    main_card_div = previous_episodes_heading.find_parent("div", class_="ln-page-card")
    if not main_card_div:
        print("Could not find the parent 'ln-page-card' for 'PREVIOUS EPISODES'.")
        return episodes_data

    episode_list_container = main_card_div.find(
        "div",
        class_=lambda c: c
        and "grid" in c
        and "grid-cols-1" in c
        and "gap-4" in c
        and "divide-y" in c
        and "mt-2" in c,
    )
    if not episode_list_container:
        print("Could not find the episode list container div for 'PREVIOUS EPISODES'.")
        return episodes_data

    episode_items = episode_list_container.find_all(
        "div", class_="pt-4", recursive=False
    )
    if not episode_items:
        print(
            "Found 'PREVIOUS EPISODES' list container, but no 'div.pt-4' items within it."
        )
        return episodes_data

    print(
        f"Found {len(episode_items)} items matching 'div.pt-4' (potential previous episodes)."
    )

    for item_div in episode_items:
        episode_detail = parse_single_episode_item(item_div, base_url)
        if episode_detail:
            # Avoid duplicates if the same link/title appears
            if not any(
                ep["link"] == episode_detail["link"]
                and ep["title"] == episode_detail["title"]
                for ep in episodes_data
            ):
                episodes_data.append(episode_detail)

    return episodes_data


def fetch_and_extract_all_episodes(podcast_url, latest_only=False):
    """
    Fetches the main podcast page and extracts both latest and previous episodes.
    Args:
        podcast_url (str): The URL of the ListenNotes podcast page.
    Returns:
        list: A list of dictionaries, where each dictionary contains
              'title' and 'link' of an episode. Latest episode is first.
    """
    all_episodes = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        print(f"Fetching {podcast_url}...")
        response = requests.get(podcast_url, headers=headers, timeout=15)
        response.raise_for_status()

        # Save HTML for inspection - helpful for debugging if live site changes
        html_file_path = "listennotes_live_page_full.html"
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(
            f"Saved full live page content to '{os.path.abspath(html_file_path)}' for inspection."
        )

        soup = BeautifulSoup(response.content, "html.parser")

        # 1. Get the latest episode
        latest_episode = parse_latest_episode_from_html(soup, base_url=podcast_url)
        if latest_episode:
            print(f"Successfully parsed LATEST episode: {latest_episode['title']}")
            all_episodes.append(latest_episode)
        else:
            print("Could not parse the LATEST episode.")

        if latest_only:
            return all_episodes

        # 2. Get previous episodes
        previous_episodes = parse_previous_episodes_from_html(
            soup, base_url=podcast_url
        )
        if previous_episodes:
            print(f"Successfully parsed {len(previous_episodes)} PREVIOUS episodes.")
            # Add previous episodes, avoiding duplication if latest was somehow also in previous
            for prev_ep in previous_episodes:
                if not any(ep["link"] == prev_ep["link"] for ep in all_episodes):
                    all_episodes.append(prev_ep)
        else:
            print("Could not parse PREVIOUS episodes or none were found.")

        return all_episodes

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


# --- Main Execution ---
if __name__ == "__main__":
    aggrolink_url = (
        "https://www.listennotes.com/podcasts/agrolink-news-agrolink-vcfmUpiP2zO/"
    )
    nytimes_url = (
        "https://www.listennotes.com/podcasts/the-daily-the-new-york-times-xp7nhsmSkX2/"
    )

    target_url = aggrolink_url

    print(f"Attempting to scrape all episodes from: {target_url}")
    extracted_episodes = fetch_and_extract_all_episodes(target_url, latest_only=True)

    if extracted_episodes:
        print(
            f"\nSuccessfully extracted a total of {len(extracted_episodes)} episodes:\n"
        )
        for i, episode in enumerate(extracted_episodes):
            print(f"{i+1}. Title: {episode['title']}")
            print(f"   Link: {episode['link']}\n")
    else:
        print("\nNo episodes were successfully extracted from the live page.")
        print(
            f"Please check '{os.path.abspath('listennotes_live_page_full.html')}' to see the content that was fetched."
        )
        print(
            "The HTML structure of the live page might differ, or the sections might be missing/changed."
        )
