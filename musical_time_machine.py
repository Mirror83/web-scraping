import sys

import requests
import re
import datetime
from bs4 import BeautifulSoup

MIN_YEAR = 1900  # An arbitrarily set value


def display_err(msg: str) -> None:
    print(msg, file=sys.stderr)
    exit(1)


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

i = 0
for h3 in all_song_title_h3:
    i += 1
    song_title = h3.get_text(strip=True)
    artist = h3.find_next_sibling("span").get_text(strip=True)
    print(f"{i}. {song_title} - {artist}")
