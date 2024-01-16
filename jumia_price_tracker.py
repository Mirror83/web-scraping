import datetime
import os
import sys

import requests
from bs4 import BeautifulSoup, Tag

import smtplib

from dotenv import load_dotenv


def get_price_float(price_span: Tag) -> float | None:
    price_text = price_span.text
    price_string = price_text.split(" ")[1].strip()

    price_string = price_string.replace(",", "")

    price = None

    try:
        price = float(price_string)
    except ValueError:
        print(f"Could not convert '{price_string}' to an integer")

    return price


def get_prices_from_soup() -> tuple[float, float]:
    details_section = get_details_section()
    prices_div = details_section.find("div", class_="-hr -mtxs -pvs")

    price_spans = prices_div.find_all("span", dir="ltr")
    # There should be two spans, one for the current price and the other for the slashed price

    current_price_span = price_spans[0]
    slashed_price_span = price_spans[1]

    current_price = get_price_float(current_price_span)
    slashed_price = get_price_float(slashed_price_span)

    if not current_price and not slashed_price:
        print("Could not find prices")
        exit(1)

    return current_price, slashed_price


def get_details_section() -> Tag:
    return soup.find("section", class_="col12 -df -d-co")


def get_product_name() -> str:
    details_section = get_details_section()
    name_h1 = details_section.find("h1")

    return name_h1.text


def send_bargain_email(current_price: float, product_name: str):
    with smtplib.SMTP(os.environ["MAIL_SERVER"]) as smtp:
        smtp.starttls()

        from_address = os.environ["FROM_ADDRESS"]
        to_address = os.environ["TO_ADDRESS"]
        smtp.login(from_address, os.environ["MAIL_PASSWORD"])

        subject = f"Jumia Price Tracker - Bargain Alert for {product_name}"
        body = (f"{product_name} is selling for Ksh.{current_price} which is Ksh.{preferred_price - current_price} "
                f"below your preferred price of Ksh.{preferred_price}. Hurry on to Jumia and snag yourself a deal!\n"
                f"The offer was discovered on {datetime.datetime.today()}")

        smtp.sendmail(from_address, to_address, msg=f"Subject:{subject}\n\n{body}")

    print("Email sent!")


load_dotenv()

# TODO: Add support for more than one product
# TODO: Extract email text into a (html) file template and replace the relevant info using code
# TODO: Remove semi-hardcoded page urls and preferred prices and use a database instead
# TODO: Perform the price against preferred price check for each of the products in the database
# TODO: Provide the user a way to add and remove products from the database
# TODO: Perform relevant error handling e.g in the case of a broken link or a website redesign
#       (in which case the class names used for scraping will not work)

preferred_price = 16_500

page_url = os.environ["JUMIA_PRODUCT_URL"]  # Download page for a Shure SM7 mic
response = requests.get(page_url)

if response.status_code != 200:
    print(f"Something went wrong. Status code: {response.status_code}", file=sys.stderr)
    exit(1)

product_page = response.text
soup = BeautifulSoup(product_page, "lxml")

curr_price, slash_price = get_prices_from_soup()

print(f"Current price: {curr_price}. Slash price: {slash_price}")

if curr_price <= preferred_price:
    send_bargain_email(curr_price, get_product_name())
else:
    print("Sorry, the price is still too high.")
