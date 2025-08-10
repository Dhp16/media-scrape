import re
import unicodedata

def sanitize_title(title_string) -> str:
    """
    Sanitizes a string to be safe for use in file paths or database table names.

    Replaces problematic characters with underscores and converts to lowercase.

    Args:
        title_string (str): The original title string (e.g., podcast episode title).

    Returns:
        str: The sanitized string.
    """
    # 1. Normalize Unicode characters to their closest ASCII equivalents
    # This helps handle characters like accented letters
    title_string = unicodedata.normalize('NFKD', title_string).encode('ascii', 'ignore').decode('ascii')

    # 2. Convert to lowercase
    title_string = title_string.lower()

    # 3. Replace spaces and hyphens with underscores (or you could just replace spaces)
    # Replacing hyphens too can simplify things if you prefer underscores
    title_string = re.sub(r'[\s-]+', '_', title_string)

    # 4. Remove characters that are generally unsafe for filenames and database tables.
    # This regex keeps letters, numbers, and underscores. You can add more if needed (e.g., hyphens).
    title_string = re.sub(r'[^a-z0-9_]', '', title_string)

    # 5. Remove leading/trailing underscores that might result from replacements
    title_string = title_string.strip('_')

    # 6. Handle potential empty strings after sanitization
    if not title_string:
        return "untitled" # Or raise an error, depending on desired behavior

    return title_string

def _test():
    # --- Example Usage ---
    podcast_episode_title = "The Best Episode: \"AI's Impact on the Future\" (Part 1/2)!"
    podcast_series_title = "My Awesome Podcast!"

    sanitized_episode_title = sanitize_title(podcast_episode_title)
    sanitized_series_title = sanitize_title(podcast_series_title)

    print(f"Original Episode Title: {podcast_episode_title}")
    print(f"Sanitized Episode Title: {sanitized_episode_title}")
    print(f"Original Series Title: {podcast_series_title}")
    print(f"Sanitized Series Title: {sanitized_series_title}")
