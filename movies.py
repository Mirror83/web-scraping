import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.empireonline.com/movies/features/best-movies-2/")

soup = BeautifulSoup(response.text, "html.parser")

all_titles = soup.select("h3.listicleItem_listicle-item__title__BfenH")

with open("fav_movies.txt", "w", encoding="utf-8") as file:
    for i in range(len(all_titles) - 1, -1, -1):
        file.write(all_titles[i].text + "\n")
