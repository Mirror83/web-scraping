contents = []

with open("website.html", encoding="utf-8") as website:
    contents.extend(website.readlines())

print(contents)
