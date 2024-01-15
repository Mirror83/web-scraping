import os
import sys

import requests
from bs4 import BeautifulSoup, Tag

from dotenv import load_dotenv

load_dotenv()

page_url = os.environ["JUMIA_PRODUCT_URL"]  # Download page for a Shure SM7 mic
response = requests.get(page_url)

if response.status_code != 200:
    print(f"Something went wrong. Status code: {response.status_code}", file=sys.stderr)
    exit(1)

product_page = response.text
soup = BeautifulSoup(product_page, "lxml")

details_section = soup.find("section", class_="col12 -df -d-co")
prices_div = details_section.find("div", class_="-hr -mtxs -pvs")

price_spans = prices_div.find_all("span", dir="ltr")
# There should be two spans, one for the current price and the other for the slashed price

current_price_span = price_spans[0]
slashed_price_span = price_spans[1]


def get_price(price_span: Tag) -> float | None:
    price_text = price_span.text
    price_string = price_text.split(" ")[1].strip()

    price_string = price_string.replace(",", "")

    price = None

    try:
        price = float(price_string)
    except ValueError:
        print(f"Could not convert '{price_string}' to an integer")

    return price


current_price = get_price(current_price_span)
slashed_price = get_price(slashed_price_span)

if current_price and slashed_price:
    print(f"Current price: {current_price}")
    print(f"Slashed price: {slashed_price}")
