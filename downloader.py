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

            # Find the <h1> tag with the show title
            title_tag = soup.find('h1', {'data-testid': 'titleScreen_descriptionCard_title'})

            if title_tag:
                # Extract show name, season number, and episode number from the tag's content
                title_text = title_tag.text
                match = re.match(r'^(.*?)\s*\|\s*Season\s*(\d+)\s*\|\s*Episode\s*(\d+)', title_text)

                if match:
                    show_name, season_number, episode_number = match.groups()

                    # Generate the filename
                    filename = f"{show_name.strip('.')}.S{season_number}.E{episode_number}.mkv"

                    print(f"Extracted {filename} from {url}")

                    # Find all MPD URLs in the HTML content
                    mpd_urls = re.findall(r'"(https://[^"]+\.mpd)"', str(soup))
                    return mpd_urls, show_name, season_number, episode_number
                else:
                    print(f"Invalid format in the <h1> tag content: {title_text}")

            else:
                print("No <h1> tag with the show title found.")

        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return [], "", "", ""  # Return empty values if extraction fails

# Define the function to download an MPD URL using yt-dlp with a custom filename format
def download_mpd_url(mpd_url, show_name, season_number, episode_number):
    try:
        # Generate the filename based on the show name, season number, and episode number
        filename = f"{show_name}.S{season_number}.E{episode_number}.mkv"

        # Construct the yt-dlp command with the custom filename
        cmd = [
            'yt-dlp',
            '--no-part',
            '--restrict-filenames',
            '-N', '4',
            '--user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0',
            '--cookies-from-browser', 'firefox',
            '--referer', 'https://www.amazon.in/',
            '--output', filename,  # Use the custom filename
            mpd_url
        ]

        # Run the yt-dlp command to download the MPD URL
        subprocess.run(cmd, check=True)
        print(f"Downloaded: {filename}")

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
        mpd_urls, show_name, season_number, episode_number = extract_mpd_urls(episode_url)
        if mpd_urls:
            for mpd_url in mpd_urls:
                download_mpd_url(mpd_url, show_name, season_number, episode_number)

print("All episodes downloaded.")
