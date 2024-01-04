from bs4 import BeautifulSoup

with open("website.html", encoding="utf-8") as file:
    contents = file.read()

soup = BeautifulSoup(contents, features="html.parser")
anchor_tags = soup.find_all(name="a")

for tag in anchor_tags:
    print(tag["href"])

heading = soup.find_all(attrs={"class": "headings"})
print(heading)

company_url = soup.select_one("p a")
print(company_url)
