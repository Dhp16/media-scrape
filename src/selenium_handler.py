import re
import requests
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from manage_podcasts.config import DOWNLOADS_FOLDER


def sanitize_filename(name: str) -> str:
    """Removes characters invalid for filenames and replaces spaces."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name.replace(" ", "_").replace(":", "_")  # Also replace colons
    return name[:150]


def download_audio_from_redirect(redirect_url: str, filepath: str):
    """
    Navigates to a redirector URL with Selenium, gets the final URL,
    and downloads the audio file with requests.
    """
    is_success = False

    # Set up a headless Chrome WebDriver
    options = Options()
    options.add_argument(
        "--headless"
    )  # Run in headless mode (without opening a browser window)
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")

    driver = webdriver.Chrome(options=options)

    print(f"Opening redirector URL: {redirect_url} with Selenium...")

    try:
        driver.get(redirect_url)

        time.sleep(5)  # TODO: Can check more specifically for page being ready

        final_url = driver.current_url  # original url was redirected, get the new url
        print(f"Final audio URL after redirection: {final_url}")

        if final_url:
            print(f"Starting download of the audio file...")

            response = requests.get(final_url, stream=True)

            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

                is_success = True
                print(f"Audio downloaded successfully as '{filepath}'.")
            else:
                print(f"Error downloading file. Status code: {response.status_code}")
        else:
            print("Could not get a final URL from the browser.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the browser is closed even if an error occurs
        driver.quit()

    return is_success


def download_audio(title, url):
    sanitized_title = sanitize_filename(title)
    fs_location = DOWNLOADS_FOLDER + sanitized_title + ".mp3"
    is_success = download_audio_from_redirect(url, fs_location)

    return fs_location if is_success else None


# --- Example Usage ---
if __name__ == "__main__":
    title = "agrinews_latest_title_placeholder"
    audio_link = "https://audio.listennotes.com/e/p/b866a4912d8f436c83ca2f7a72f3ef87/"

    download_audio(title, audio_link)
