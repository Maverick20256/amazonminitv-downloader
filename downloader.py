import subprocess
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor

# Define the function to extract MPD URLs from a given URL
def extract_mpd_urls(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all MPD URLs in the HTML content
            mpd_urls = re.findall(r'"(https://[^"]+\.mpd)"', str(soup))
            return mpd_urls
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

# Define the function to download an MPD URL using yt-dlp
def download_mpd_url(mpd_url):
    try:
        # Construct the yt-dlp command
        cmd = [
            'yt-dlp',
            '--no-part',
            '--restrict-filenames',
            '-N', '4',
            '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0',
            '--cookies-from-browser', 'firefox',
            '--referer', 'https://www.amazon.in/',
            mpd_url
        ]

        # Run the yt-dlp command to download the MPD URL
        subprocess.run(cmd, check=True)
        print(f"Downloaded: {mpd_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {mpd_url}: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Read episode URLs from the text file
with open('episode_urls.txt', 'r') as file:
    episode_urls = file.read().splitlines()

# Extract and download MPD URLs in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    for episode_url in episode_urls:
        mpd_urls = extract_mpd_urls(episode_url)
        if mpd_urls:
            executor.map(download_mpd_url, mpd_urls)

print("All episodes downloaded.")
