import requests
import xml.etree.ElementTree as ET

# Конфигурация
SUPPLIER_URL = "https://b2b.altsest.ua/cabinet/product-feed"
MASTER_SKUS_FILE = "master_skus.txt"
OUTPUT_FILE = "gardena_stock.xml"

def update_stocks():
    # 1. Загружаем Master-список артикулов
    with open(MASTER_SKUS_FILE, "r") as f:
        master_skus = [line.strip() for line in f if line.strip()]

    # 2. Скачиваем XML поставщика
    response = requests.get(SUPPLIER_URL)
    root = ET.fromstring(response.content)

    # 3. Собираем данные от поставщика (только Gardena)
    supplier_stock = {}
    for offer in root.findall(".//offer"):
        vendor = offer.find("vendor").text if offer.find("vendor") is not None else ""
        if vendor == "Gardena":
            article = offer.find("article").text
            stock = offer.find("stock_quantity").text if offer.find("stock_quantity") is not None else "0"
            supplier_stock[article] = stock

    # 4. Формируем новый XML
    new_root = ET.Element("yml_catalog")
    shop = ET.SubElement(new_root, "shop")
    offers = ET.SubElement(shop, "offers")

    for sku in master_skus:
        offer = ET.SubElement(offers, "offer", id=sku.replace(".", "")) # ID без точек для валидности
        ET.SubElement(offer, "article").text = sku
        ET.SubElement(offer, "vendor").text = "Gardena"
        
        # Если артикул есть у поставщика — берем его остаток, иначе — 0
        current_stock = supplier_stock.get(sku, "0")
        ET.SubElement(offer, "stock_quantity").text = current_stock

    # 5. Сохраняем файл
    tree = ET.ElementTree(new_root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Файл {OUTPUT_FILE} успешно обновлен.")

if __name__ == "__main__":
    update_stocks()
