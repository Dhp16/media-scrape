import time
import os
import shutil # To potentially move the file later
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
# IMPORTANT: Replace with the ACTUAL audio URL you have
# file_url = "https://stitcher2.acast.com/livestitches/ce232dc50aae08c7d491f31915013070.mp3?aid=68141ae39704d99f84d9fd92&chid=73fe3ede-5c5c-4850-96a8-30db8dbae8bf&ci=X15MX5VTTj4fyXmYJzs3gdWtSbQ7ps3wZszJlhefu7b0C_mhsyewAQ%3D%3D&pf=rss&range=bytes%3D0-&sv=sphinx%401.236.0&uid=a2968d2480bac46994f0a2d23ab9d36a&Expires=1746392859613&Key-Pair-Id=K38CTQXUSD0VVB&Signature=c0uzXJxAQKiLNUaV8DYlGYHmZvqDAqQdB6r-yNaIw83w-pSKXleG5ghwWPHHP6cmT3NGERj6lWA~co4lVJqaCgHjbjswH2q1qUmbt1rEwCcFCidvc19Ca0So7ddoBtgxkrroB0qDMrqKzCFqYCgHDcH-tVgK3~LvqlLCinAghIEjQZcNjGlPiIYVoEE780lODrPI0z7IIxpKBGFbMkRGPW3xgwbnCMj7ZDo~LgWXScJh9~4mYFlwm1uafRM9kiwQYNhsplHUXbfHBn62hM3TxHNfjqjMO4hrcgV47Pukwt7-6WVxSPbXASrHx8VZFbwkmZCZ7eGPwBB1pLX41uZmxw__"

# file_url = "https://audio.listennotes.com/e/p/732dec567f6b46a59365bb060b4be49c/?_gl=1*1j0914r*_gcl_au*NDA0NzM5MC4xNzQ2MzgwMzI5*_ga*ODYxOTIwODYyLjE3NDYzODA1OTY.*_ga_T0PZE2Z7L4*czE3NDY1NjIwNzgkbzIkZzEkdDE3NDY1NjIxMDUkajMzJGwwJGgw"

def _move_file(source_dir: str, desired_dir: str, desired_file_name: str):
    # Ensure the target directory exists
    os.makedirs(desired_dir, exist_ok=True)

    try:
        # List files in the source directory
        files_in_source = os.listdir(source_dir)

        # Check if there is exactly one file in the source directory
        if len(files_in_source) == 0:
            print(f"Error: The source directory '{source_dir}' is empty.")
        elif len(files_in_source) > 1:
            print(f"Error: More than one file found in the source directory '{source_dir}'.")
            print("Please ensure only one file is present.")
        else:
            # Get the name of the single file
            original_filename = files_in_source[0]

            # Construct the full path for the source file
            source_path = os.path.join(source_dir, original_filename)

            # Construct the full path for the destination file (in the target directory with the new name)
            target_path = os.path.join(desired_dir, desired_file_name)

            # Use shutil.move() to move and rename the file
            # shutil.move(src, dst) will move the file from src to dst.
            # If dst is a directory, the file is moved into that directory.
            # If dst is a file path, the file is moved *to* that path (effectively renaming it).
            shutil.move(source_path, target_path)

            print(f"Successfully moved '{source_path}' to '{target_path}'")

            return target_path

    except FileNotFoundError:
        print(f"Error: The source directory '{source_dir}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None


def download_file(file_url: str, desired_dir: str, desired_file_name: str):

    # --- Set up a dedicated download directory ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(script_dir, "selenium_downloads")
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    print(f"Configuring downloads to: {download_dir}")

    # --- Configure Chrome Options for Automatic Download ---
    chrome_options = Options()
    # Run headless if you don't need to see the browser window
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    prefs = {
        "download.default_directory": download_dir, # Set download path
        "download.prompt_for_download": False,  # Disable prompt
        "download.directory_upgrade": True,     # Allow download path changes
        "plugins.always_open_pdf_externally": True, # Helps sometimes for other types too
        "safeBrowse.enabled": True            # Keep safe Browse (can sometimes interfere if false)
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # --- Initialize WebDriver ---
    print("Initializing WebDriver with download preferences...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # --- Expected filename (heuristic - might need adjustment) ---
    # Browsers often derive filename from URL or Content-Disposition header
    # We'll assume it might be derived from the last part of the URL for waiting
    expected_filename_part = os.path.basename(file_url).split('?')[0] # Basic guess
    if not expected_filename_part:
         expected_filename_part = "downloaded_audio" # Fallback guess
    print(f"Will look for downloaded file containing: '{expected_filename_part}'")

    download_complete = False
    downloaded_file_path = None

    try:
        # --- Navigate & Trigger Download via JavaScript ---
        print(f"Navigating to audio URL: {file_url}")
        driver.get(file_url)
        # Wait a moment for the page (player) to potentially load
        time.sleep(5) # Adjust if needed

        print("Attempting to trigger download via JavaScript...")
        # This JS creates a hidden link with the 'download' attribute and clicks it
        js_download_script = f"""
            var url = window.location.href; // Use current URL
            var link = document.createElement('a');
            link.href = url;
            // Try setting a default filename (browser might override)
            link.download = '{os.path.basename(file_url).split("?")[0] or "audio.mp3"}';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """
        driver.execute_script(js_download_script)
        print("JavaScript download trigger executed.")

        # --- Wait for Download to Complete ---
        print(f"Waiting for download to complete in '{download_dir}'...")
        max_wait_time_seconds = 120 # Wait for max 2 minutes
        start_time = time.time()
        temp_download_extension = ".crdownload" # Chrome's temporary download file extension

        while time.time() - start_time < max_wait_time_seconds:
            found_file = False
            all_files = os.listdir(download_dir)
            active_downloads = [f for f in all_files if f.endswith(temp_download_extension)]

            if not active_downloads:
                # Check if a potential final file exists
                for filename in all_files:
                     # Check if the expected part is in filename and it's NOT a temp file
                    if expected_filename_part.lower() in filename.lower() and not filename.endswith(temp_download_extension):
                        downloaded_file_path = os.path.join(download_dir, filename)
                        # Optional: Add a small delay and check file size stability if needed
                        time.sleep(2) # Small delay to ensure writing is finished
                        print(f"Download likely complete: {filename}")
                        download_complete = True
                        break # Exit inner loop

            if download_complete:
                break # Exit outer loop

            # Wait before checking again
            time.sleep(2)

        if not download_complete:
            print(f"Download did not complete within {max_wait_time_seconds} seconds.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # --- Cleanup ---
        print("Closing browser.")
        if driver:
            driver.quit()

    # --- Post-Download ---
    if downloaded_file_path and os.path.exists(downloaded_file_path):
        print(f"File successfully downloaded to: {downloaded_file_path}")
    else:
        print("Failed to confirm downloaded file path.")

    return _move_file(download_dir, desired_dir, desired_file_name)
