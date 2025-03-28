from bs4 import BeautifulSoup
import requests
from django.db import transaction
from products.models import Product



def format_price(price_text):
    """
    Formats the price string to a float.
    :param price_text: price string
    :return: formatted price as float
    """

    # Удаляем евро, дефис, неразрывный пробел
    price_text = price_text.replace('€', '').replace('-', '').replace('\xa0', '').strip()

    # Удаляем точки-разделители тысяч
    price_text = price_text.replace('.', '')

    # Заменяем запятую на точку
    price_text = price_text.replace(',', '.')

    # Удаляем точку в конце, если она одна и последняя
    if price_text.count('.') == 1 and price_text.endswith('.'):
        price_text = price_text[:-1]

    return price_text


def get_link_data(url):
    """
    Получает данные о продукте по ссылке.
    :param url: URL продукта
    :return: кортеж с данными о продукте (название, цена, фото, базовый URL, поставщик, URL поставщика, описание)
    """
    if not url:
        return "", None, "", "", "", "", ""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.1 Safari/605.1.15",
        "Accept-Language": "en-GB,en;q=0.9",
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "", None, "", "", "", "", ""

    soup = BeautifulSoup(response.text, "html.parser")
    if not soup:
        return "", None, "", "", "", "", ""

    base_url = url

    # Изображение товара
    img_tag = soup.select_one("div.gallery-trigger img")
    photo_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

    # Название товара
    name_block = soup.find("h1", class_="line-clamp")
    name = name_block.get_text(strip=True) if name_block else ""

    # Цена
    price = None
    price_tag = soup.find("span", class_="lowest-price")
    if price_tag:
        price = format_price(price_tag.get_text(strip=True))

    # Поставщик
    supplier_block = soup.find("span", class_="ellipsis")
    supplier = supplier_block.get_text(strip=True) if supplier_block else ""

    # Ссылка на поставщика
    supplier_block_url = soup.find("a", class_="price")
    supplier_url = supplier_block_url["href"] if supplier_block_url and supplier_block_url.has_attr("href") else ""

    # Описание
    description = ""
    all_specs = soup.find_all("div", class_="spec-content spec-line")
    for spec in all_specs:
        description_block = spec.find("a", class_="line-clamp")
        if description_block:
            description = description_block.get_text(strip=True)
            break  # Берем первое найденное описание и выходим

    return name, price, photo_url, base_url, supplier, supplier_url, description

# def get_link_data(url):
    """
    Gets the product data from the link.
    :param url: product URL
    :return: tuple with product data (title, price, photo, base URL, supplier, supplier URL, description)
    """
    
    if url is None:
        return None, 0.0, None, None, None, None, None


    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/16.1 Safari/605.1.15",
        "Accept-Language": "en-GB,en;q=0.9",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    if soup:
        base_url = url


        img_tag = soup.select_one('div.gallery-trigger img')
        photo_url = img_tag['src'] if img_tag else None

        product_name_block = soup.find("h1", class_="line-clamp").get_text(strip=True)
        name = product_name_block if product_name_block else None

        price = 0.0
        price_tag = soup.find("span", class_="lowest-price")
        if price_tag:
            price_text = price_tag.get_text(strip=True)
            try:
                price = float(format_price(price_text))
            except ValueError:
                price = 0.0

        supplier_block = soup.find("span", class_="ellipsis").get_text(strip=True)
        supplier = supplier_block if supplier_block else None

        supplier_block_url = soup.find("a", class_="price").get('href')
        supplier_url = supplier_block_url if supplier_block_url else None

        all_specs = soup.find_all("div", class_="spec-content spec-line")
        for spec in all_specs:
            description_block = spec.find("a", class_="line-clamp")

            description = description_block.get_text(strip=True) if description_block else None

        return name, price, photo_url, base_url, supplier, supplier_url, description

    return None, 0.0, None, None, None, None, None



def save_product_data(url):
    """Saves the product data to the database."""
    
    data = get_link_data(url)

    # Создаем новый объект с актуальными данными
    product = Product.objects.create(
        name=data[0],
        price=data[1],
        photo_url=data[2],
        product_url=url,
        supplier=data[4],
        supplier_url=data[5],
        description=data[6],
    )

    created = True

    return product, created



def update_all_product_data():
    """
    Updates all product data in the database.
    :return: None
    """


    all_urls = Product.objects.values_list('product_url', flat=True).distinct()

    for url in all_urls:
        name, price, photo_url, _, supplier, supplier_url, description = get_link_data(url)

        # Создаем новую запись для каждого парсинга
        with transaction.atomic():  # Обеспечиваем атомарность транзакции
            Product.objects.create(
                product_url=url,
                name=name,
                price=price,
                photo_url=photo_url,
                supplier=supplier,
                supplier_url=supplier_url,
                description=description,
            )

            print(f"Added new product from URL: {url}")


def delete_products_by_url(url):
    """
    Deletes all products with the given URL from the database.
    :param url: product URL
    :return: None
    """

    # Находим все записи с данным URL и удаляем их
    products_to_delete = Product.objects.filter(product_url=url)
    
    # Если есть записи с данным URL, удаляем их
    if products_to_delete.exists():
        products_to_delete.delete()
        print(f"All product from URL: {url} deleted.")
    else:
        print(f"Product from URL: {url} not found.")



# print(get_link_data('https://tweakers.net/pricewatch/2108170/benq-ma270u-zilver.html'))
# print(get_link_data('https://tweakers.net/pricewatch/2108172/benq-ma320u-zilver.html'))
# print(get_link_data('https://tweakers.net/pricewatch/2158582/dell-ultrasharp-u3225qe-zwart.html'))

# https://tweakers.net/pricewatch/2182528/apple-mac-studio-2025-m4-max-14-core-36gb-ram-32-core-gpu-512gb-ssd.html