import os
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

def download_pages(base_url, start_page, end_page):
    for page in range(start_page, end_page + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            with open(f'page_{page}.html', 'w', encoding='utf-8') as file:
                file.write(soup.prettify())
            print(f"Downloaded page {page}")
        else:
            print(f"Failed to download page {page}")

# base_url = "https://litemf.com/ru/shop"
# download_pages(base_url, 1, 58)




data = [
    ('electronics', 'Электроника'),
    ('shopping-malls', 'Шоппинг-моллы'),
    ('hobbies', 'Хобби и активный отдых'),
    ('clothing-and-footwear-for-sport', 'Одежда и обувь для занятий спортом'),
    ('shoes', 'Обувь'),
    ('clothing-footwear-and-accessories', 'Одежда, обувь, аксессуары'),
    ('clothing-and-footwear-premium', 'Одежда и обувь класса Premium'),
    ('underwear-and-intimate', 'Нижнее белье и интимные товары'),
    ('for-children-and-mothers', 'Товары для детей'),
    ('homeware', 'Товары для дома'),
    ('cosmetics-perfumes-intimate', 'Косметика, парфюмерия, интимные товары'),
    ('musical-instruments', 'Музыкальные инструменты'),
    ('auto-parts', 'Автозапчасти'),
    ('toys', 'Игрушки')
]

from bs4 import BeautifulSoup

collected_hrefs = []


def collect_categories_data(category='electronics',page=1):
    """https://litemf.com/ru/shop/electronics?&page=1"""
    url = f"https://litemf.com/ru/shop/{category}?&page={page}"

    request = requests.get(url)
    if request.status_code != 200:
        print(request.text)
        print('wrong')
    soup = BeautifulSoup(request.content, 'html.parser')
    print(len(soup))
    os.makedirs(f'category/{category}', exist_ok=True)

    # Записываем HTML в файл
    with open(f'category/{category}/page_{category}_{page}.html', 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
        print('saved {}'.format(f'category/{category}/page_{category}_{page}.html'))

    page_links = soup.find_all('a', class_='page-link')
    print(page_links)

    for num,page in enumerate(page_links):
        if page:
            link = page.get('href')
            tag = page.get('aria-label')
            print(num,link,tag)
            if tag == 'Next':
                print(link)
                parsed_url = urlparse(link)
                params = parse_qs(parsed_url.query)
                page_number = params.get("page", [""])[0]
                page_number=int(page_number)
                print('ding',page_number)
                collect_categories_data(category=category,page=page_number)

def main_category_parsing():
    for category, _ in data:
        collect_categories_data(category=category)

























