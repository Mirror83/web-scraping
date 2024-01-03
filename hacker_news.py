"""
Currently prints the information on the article with the most votes
in Hacker News. Can be modified to do more.
"""

import requests
from bs4 import BeautifulSoup

response = requests.get(url="https://news.ycombinator.com/")

soup = BeautifulSoup(response.text, features="html.parser")

all_title_trs = soup.select("tr.athing")


article_links = []
article_titles = []
article_votes = []

for tr in all_title_trs:
    anchor_tag = tr.select_one("td.title span.titleline a")
    article_title = anchor_tag.text
    article_link = anchor_tag["href"]

    upvote_tr = tr.next_sibling
    score_span = upvote_tr.find_next("span", class_="score")

    article_links.append(article_link)
    article_titles.append(article_title)

    if score_span is not None:
        score_text = score_span.text
        score = int(score_text.split(" ")[0])
        article_votes.append(score)


max_vote = max(article_votes)
max_vote_index = article_votes.index(max_vote)

print(f"Max vote: {max_vote}")
print(f"Article number {max_vote_index + 1}")
print(article_titles[max_vote_index])
print(article_links[max_vote_index])
