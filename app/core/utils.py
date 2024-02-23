import os
import csv
from django.conf import settings

BOOK_METADATA_CSV = os.path.join(settings.DATA_DIR, "book_dataset.csv" )


def load_book_data():
    dataset = []
    with open(BOOK_METADATA_CSV, newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                price = row.get("price")
                price = price.removeprefix("US$")
                price = float(price)
            except Exception as e:
                continue
            data = {
                'name': row.get("name", None),
                'author': row.get("author", None),
                'category': row.get("category", None),
                'isbn': row.get("isbn", None),
                'format': row.get("format", None),
                'ratings': row.get("book_depository_stars", None),
                'book_covers_directory': os.path.join(settings.DATA_DIR, row.get("img_paths")),
                'price':  price,
            }
            dataset.append(data)
    return dataset
