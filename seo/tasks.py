import os

from bs4 import BeautifulSoup
from celery import shared_task
from django.db import transaction

from app_front.management.email.email_sender import my_logger
from seo.models import ShopItem, ShopCategory
from shipkz.settings import BASE_DIR


def extract_all_links():
    collected_hrefs = []

    for i in range(1, 59):
        with open(f"parsing/page_{i}.html", "r", encoding="utf-8") as file:
            data = file.read()
            soup = BeautifulSoup(data, 'html.parser')
            nav_div = soup.find('div', class_='index')
            rows = nav_div.find_all('a', class_='link')
            for num, row in enumerate(rows, start=1):
                collected_hrefs.append(row.text.strip())

    for i,row in enumerate(collected_hrefs):
        print(f"{i},{row}")
    return collected_hrefs


@shared_task
def extract_links_task():
    bulk_create = []
    data = extract_all_links()
    for link in data:
        link_address = f"https://{link}"
        new_link = ShopItem(name=link,link_name=link,link_address=link_address,)
        bulk_create.append(new_link)

    ShopItem.objects.bulk_create(bulk_create, ignore_conflicts=True,batch_size=1000)

@shared_task
def extract_links_with_categories_task():
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
    collected_hrefs = []
    for category, russian_name in data:
        dir_path = os.path.join(BASE_DIR,"parsing", "category", category)  # Абсолютный путь к папке
        my_logger.info(dir_path)

        dir_names = os.listdir(dir_path)
        for file_name in dir_names:
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    nav_div = soup.find('div', class_='index')
                    if nav_div:
                        rows = nav_div.find_all('a', class_='link')
                        for row in rows:
                            collected_hrefs.append((row.text.strip(),category,russian_name))

    my_logger.info(f"collected_hrefs: {collected_hrefs}")
    existed_links = ShopItem.objects.values_list('name', flat=True)

    bulk_create = []

    for href, category,category_rus in collected_hrefs:
        category_obj = ShopCategory.objects.filter(name=category).first()
        if href not in existed_links:
            my_logger.info(f'create_link {href}')
            if category_obj:
                new_link = ShopItem(name=href,
                                    link_name=href,
                                    link_address=f"https://{href}",
                                    category=category_obj)
                bulk_create.append(new_link)
            else:
                new_category=ShopCategory.objects.create(name=category,name_rus=category_rus)
                new_link = ShopItem(name=href,
                                    link_name=href,
                                    link_address=f"https://{href}",
                                    category=new_category)
                bulk_create.append(new_link)
        else:
            my_logger.info(f'update link{href}')
            if category_obj:
                old_link = ShopItem.objects.filter(name=href).first()
                old_link.category = category_obj
                old_link.save()
    ShopItem.objects.bulk_create(bulk_create, ignore_conflicts=True, batch_size=1000)
    return "task complete"


@shared_task
def add_custom_categories():

    # Данные для категорий
    categories = [
        {   "name": "tool",
            "name_rus":"Автозапчасти и мотозапчасти",
            "items" :  [
            "rockauto.com", "ebay.com", "ebay.de", "ebay.co.uk", "amazon.com", "amazo.de",
            "carid.com", "harley-davidson.com", "gmpartsgiant.com", "partsgeek.com", "optionsauto.com",
            "advanceautoparts.com", "ford.oempartsonline.com", "buywitchdoctors.com", "indianmotorcycle.com",
            "thunderbike.com", "fc-moto.de"
        ]
    },
        {
        "name": "vinyl",
        "name_rus":"Виниловые пластинки",
        "items" : [
        "discogs.com", "ebay.com", "amazon.com", "amazon.de", "hhv.de", "chloeslater.tmstor.es",
        "roughtrade.com", "juno.co.uk", "saint-etienne-official.com", "nuclearblast.com", "napalmrecords.com",
        "lptunes.com", "zedsdead-records.com", "lacrimosa.hamburgrecords.com", "backwoodzstudioz.com",
        "season-of-mist.com", "purity-through-fire.com", "cdjapan.co.jp", "justforkicks.de", "outofline.de"
        ]},
        {
        "name": "instrument",
        "name_rus":"Инструменты",
        "items" : [
        "amazon.com", "ebay.com", "Tools-Plus.com", "Acmetools.com", "Maxtool.com", "Homedepot.com",
        "protilertools.co.uk", "ToolDiscounter.com", "PacificToolandGauge.com", "Trick-Tools.com",
        "NorthernTool.com", "leevalley.com"
        ]}
    ]


    with transaction.atomic():
        for row in categories:
            category_name = row.get('name')
            category_rus = row.get('name_rus')
            items_links = row.get('items')

            category = ShopCategory.objects.create(
                name=category_name,
                name_rus=category_rus
            )
            for i, link in enumerate(items_links):
                suff = category_name[0]
                name = link.replace(".","")
                name = name + suff
                ShopItem.objects.create(
                    category=category,
                    name=name,  # добавляем уникальный символ
                    link_address=f"https://{link}",
                    link_name=link,
                    is_active=True
                )
    return 'complite'


@shared_task
def check_timer_tasks():
    return "hello"