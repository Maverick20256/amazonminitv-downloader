import subprocess
import requests
from bs4 import BeautifulSoup
import re
import os

m3u8DL_RE = 'N_m3u8DL-RE'

def extract_mpd_url(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the <h1> tag with the show title
            title_tag = soup.find('h1', {'data-testid': 'titleScreen_descriptionCard_title'})

            if title_tag:
                # Extract show name, season number, and episode number from the tag's content
                title_text = title_tag.text
                match = re.match(r'^(.*?)\s*\|\s*Season\s*(\d+)\s*\|\s*Episode\s*(\d+)', title_text)
                
                if match:
                    show_name, season_number, episode_number = match.groups()
                    
                    # Generate the filename
                    filename = f"{show_name.strip('.')}.S{season_number}.E{episode_number}"

                    print(f"Extracted {filename} from {url}")
                    
                    # Find the MPD URL in the HTML content using a regular expression
                    mpd_url_match = re.search(r'"(https://[^"]+\.mpd)"', str(soup))
                    
                    if mpd_url_match:
                        mpd_url = mpd_url_match.group(1)
                        print(f"Downloading {filename} from {mpd_url}")

                        # Run m3u8DL-RE to download the episode
                        subprocess.run([m3u8DL_RE,
                                        '-M', f'format=mkv:muxer=ffmpeg:quality={quality}',
                                        '--concurrent-download',
                                        '--log-level', 'INFO',
                                        '--save-name', filename, mpd_url])
                    else:
                        print("MPD URL not found on the page.")
                else:
                    print(f"Invalid format in the <h1> tag content: {title_text}")
            else:
                print("No <h1> tag with the show title found.")
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Read episode URLs from the text file
with open('episode_urls.txt', 'r') as file:
    episode_urls = file.read().splitlines()

# Specify the desired video quality (e.g., hd, sd)
quality = 'hd'

# Download the episodes using m3u8DL-RE
for episode_url in episode_urls:
    extract_mpd_url(episode_url)

print("All episodes downloaded.")
