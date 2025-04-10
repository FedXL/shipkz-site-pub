from bs4 import BeautifulSoup



collected_hrefs = []
for i in range(1, 59):
    with open(f"page_{i}.html", "r", encoding="utf-8") as file:
        data = file.read()
        soup = BeautifulSoup(data, 'html.parser')
        nav_div = soup.find('div', class_='index')
        rows = nav_div.find_all('a', class_='link')
        for num, row in enumerate(rows, start=1):
            collected_hrefs.append(row.text.strip())

for i,row in enumerate(collected_hrefs):
    print(f"{i},{row}")

