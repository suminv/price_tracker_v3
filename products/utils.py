from bs4 import BeautifulSoup
import requests
from django.db import transaction
from products.models import Product
from fake_useragent import UserAgent




def get_random_user_agent():
    """
    Returns a random user agent string using fake_useragent.
    :return: random user agent string
    """
    ua = UserAgent()
    return ua.random

print(get_random_user_agent())


def format_price(price_text):
    """
    Formats the price string to a float.
    :param price_text: price string
    :return: formatted price as float
    """

    price_text = price_text.replace('€', '').replace('-', '').replace('\xa0', '').strip()
    price_text = price_text.replace('.', '')
    price_text = price_text.replace(',', '.')

    if price_text.count('.') == 1 and price_text.endswith('.'):
        price_text = price_text[:-1]

    return price_text


def get_link_data(url):
    """
    Gets product data from a link.
    param url: product URL
    return: tuple with product data (name, price, photo, base URL, supplier, supplier URL, description)
    """
    if not url:
        return "", None, "", "", "", "", ""

    headers = {
        
        "User-Agent": get_random_user_agent(),

        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        return "", None, "", "", "", "", ""

    soup = BeautifulSoup(response.text, "html.parser")
    if not soup:
        return "", None, "", "", "", "", ""

    base_url = url

    img_tag = soup.select_one("div.gallery-trigger img")
    photo_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

    name_block = soup.find("h1", class_="line-clamp")
    name = name_block.get_text(strip=True) if name_block else ""

    price = None
    price_tag = soup.find("span", class_="lowest-price")
    if price_tag:
        price = format_price(price_tag.get_text(strip=True))

    supplier_block = soup.find("span", class_="ellipsis")
    supplier = supplier_block.get_text(strip=True) if supplier_block else ""

    supplier_block_url = soup.find("a", class_="price")
    supplier_url = supplier_block_url["href"] if supplier_block_url and supplier_block_url.has_attr("href") else ""

    description = ""
    all_specs = soup.find_all("div", class_="spec-content spec-line")
    for spec in all_specs:
        description_block = spec.find("a", class_="line-clamp")
        if description_block:
            description = description_block.get_text(strip=True)
            break  

    return name, price, photo_url, base_url, supplier, supplier_url, description


def save_product_data(url):
    """Saves the product data to the database."""
    
    data = get_link_data(url)

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

        with transaction.atomic():
            Product.objects.create(
                product_url=url,
                name=name,
                price=price,
                photo_url=photo_url,
                supplier=supplier,
                supplier_url=supplier_url,
                description=description,
            )

            print(f"Updated product from URL: {url}")


def delete_products_by_url(url):
    """
    Deletes all products with the given URL from the database.
    :param url: product URL
    :return: None
    """

    products_to_delete = Product.objects.filter(product_url=url)
    
    if products_to_delete.exists():
        products_to_delete.delete()
        print(f"All product from URL: {url} deleted.")
    else:
        print(f"Product from URL: {url} not found.")

