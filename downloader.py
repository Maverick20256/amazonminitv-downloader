import subprocess
import requests
from bs4 import BeautifulSoup
import re

m3u8DL_RE = 'N_m3u8DL-RE'

def extract_mpd_url(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the MPD URL in the HTML content using a regular expression
            mpd_url_match = re.search(r'"(https://[^"]+\.mpd)"', str(soup))

            if mpd_url_match:
                mpd_url = mpd_url_match.group(1)
                return mpd_url
            else:
                print(f"MPD URL not found on the page: {url}")
                return None
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# Read episode URLs from the text file
with open('episode_urls.txt', 'r') as file:
    episode_urls = file.read().splitlines()

# Specify the desired video quality (e.g., hd, sd)
quality = 'hd'

mpd_urls = []  # Store the extracted MPD URLs

for episode_url in episode_urls:
    mpd_url = extract_mpd_url(episode_url)

    if mpd_url:
        print(f"MPD URL extracted from {episode_url}: {mpd_url}")
        mpd_urls.append(mpd_url)

# Download the episodes using m3u8DL-RE
for mpd_url in mpd_urls:
    subprocess.run([m3u8DL_RE,
                    '-M', f'format=mkv:muxer=ffmpeg:quality={quality}',
                    '--concurrent-download',
                    '--log-level', 'INFO',
                    '--save-name', 'video', mpd_url])

print("All episodes downloaded.")
