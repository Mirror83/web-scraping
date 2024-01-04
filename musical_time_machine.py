import datetime
import re
import sys

import dotenv
import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy import SpotifyOAuth

MIN_YEAR = 1900  # An arbitrarily set value


def display_err(msg: str) -> None:
    print(msg, file=sys.stderr)
    exit(1)


print(dotenv.load_dotenv(".env"))

date_string = input("Which date would you like to travel to? Type the date in the format YYYY-MM-DD: ")
date_string = date_string.strip()

if not re.compile("^\\d{4}-\\d{2}-\\d{2}$").match(date_string):
    display_err(f"{date_string} is not in the required format. Please try again")

[year, month, day] = date_string.split("-")

if int(year) < MIN_YEAR:
    display_err(f"The year in {date_string} is earlier than the minimum year {MIN_YEAR}")

date = None
try:
    date = datetime.date(int(year), int(month), int(day))
except ValueError:
    display_err(f"{date_string} is an invalid date.")

if date > datetime.date.today():
    display_err(f"{date_string} is in the future.")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date_string}/")
soup = BeautifulSoup(response.text, "lxml")

all_song_title_h3 = soup.select("li.o-chart-results-list__item h3#title-of-a-story")

song_title_list = []
artist_list = []

i = 0
for h3 in all_song_title_h3:
    i += 1

    song_title = h3.get_text(strip=True)
    song_title_list.append(song_title)

    artist = h3.find_next_sibling("span").get_text(strip=True)
    artist_list.append(artist)

    print(f"{i}. {song_title} - {artist}")

scope = "playlist-modify-private"
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user = spotify.me()

search_results = [
    spotify.search(f"track:{song_title} year:{year}",
                   type="track", limit=1)
    for song_title in song_title_list]

track_uris = []
for search_result in search_results:
    for item in search_result["tracks"]["items"]:
        # TODO: Find a way to match the correct artists to each song
        track_uris.append(item["uri"])

print(track_uris)

playlist = spotify.user_playlist_create(user["id"], f"{date_string} Top 100",
                                        description=f"The Billboard Top 100 tracks from {date_string}",
                                        public=False)

print(playlist)

spotify.playlist_add_items(playlist["id"], track_uris)
