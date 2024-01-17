import dataclasses
import datetime
import os
import smtplib
import sys

import requests
from bs4 import Tag, BeautifulSoup
from dotenv import load_dotenv

import email


@dataclasses.dataclass
class BargainEmailData:
    to_address: str
    product_name: str
    product_url: str
    preferred_price: int
    current_price: float


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


def get_prices_from_soup(soup: BeautifulSoup) -> tuple[float, float]:
    details_section = get_details_section(soup)
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


def get_details_section(soup: BeautifulSoup) -> Tag:
    return soup.find("section", class_="col12 -df -d-co")


def get_product_name(soup: BeautifulSoup) -> str:
    details_section = get_details_section(soup)
    name_h1 = details_section.find("h1")

    return name_h1.text


def send_bargain_email(template_file: str | os.PathLike, data: BargainEmailData):
    with smtplib.SMTP(os.environ["MAIL_SERVER"]) as smtp:
        smtp.starttls()

        from_address = os.environ["FROM_ADDRESS"]
        to_address = data.to_address
        smtp.login(from_address, os.environ["MAIL_PASSWORD"])

        msg = email.message.EmailMessage()

        subject = f"Jumia Price Tracker - Bargain Alert for {data.product_name}"
        body = fill_template(template_file, data)
        msg["subject"] = subject
        msg.set_type("text/html")
        msg.add_attachment(body, subtype="html")

        smtp.send_message(msg, from_address, to_address)

    print("Email sent!")


def get_product_page(page_url: str) -> str:
    response = requests.get(page_url)

    if response.status_code != 200:
        print(f"Something went wrong. Status code: {response.status_code}", file=sys.stderr)
        exit(1)

    return response.text


def fill_template(template_path: str | os.PathLike[str], data: BargainEmailData) -> str:
    with open(template_path, "r") as t_file:
        contents = t_file.read()
        price_difference = data.preferred_price - data.current_price

        contents = contents.replace("{to_address}", data.to_address) \
            .replace("{product_name}", data.product_name) \
            .replace("{product_url}", data.product_url) \
            .replace("{current_price}", str(data.current_price)) \
            .replace("{preferred_price}", str(data.preferred_price)) \
            .replace("{price_difference}", str(price_difference)) \
            .replace("{today_date}", str(datetime.datetime.today()))

    return contents


load_dotenv()

# TODO: 1. Extract email text into a (html) file template and replace the relevant info using code
# TODO: 2. Add support for more than one product
# TODO: 3. Remove semi-hardcoded page urls and preferred prices and use a database instead
# TODO: 4. Perform the price against preferred price check for each of the products in the database
# TODO: 5. Provide the user a way to add and remove products from the database
# TODO: 6. Perform relevant error handling e.g in the case of a broken link or a website redesign
#       (in which case the class names used for scraping will not work)

pref_price = 1_200

url = os.environ["JUMIA_PRODUCT_URL"]
page = get_product_page(url)
soup = BeautifulSoup(page, "lxml")

name = get_product_name(soup)
curr_price, slash_price = get_prices_from_soup(soup)

print(f"Current price: {curr_price}. Slash price: {slash_price}")

email_data = BargainEmailData(os.environ["TO_ADDRESS"], name, url, pref_price, curr_price)

if curr_price <= pref_price:
    send_bargain_email("email_template.html", email_data)
else:
    print("Sorry, the price is still too high.")
