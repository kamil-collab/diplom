import pandas as pd
from backend.models.models import Company, Product, ClientInfo
import os
import requests
from sqlalchemy.orm import Session
from urllib.parse import quote

IMAGE_DIR = "static/images"

def fetch_image(query: str):
    filename = f"{query.replace(' ', '_')}.jpg"
    rel_path = f"static/images/{filename}"
    abs_path = os.path.join(IMAGE_DIR, filename)

    # Если файл уже есть, не качаем заново
    if os.path.exists(abs_path):
        return rel_path

    url = f"https://source.unsplash.com/featured/?{quote(query)}"
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(IMAGE_DIR, exist_ok=True)
        with open(abs_path, "wb") as f:
            f.write(response.content)
        return rel_path
    return None


def import_products_from_excel(path: str, session: Session):
    df = pd.read_excel(path)

    # Клиентская информация
    client_row = df.iloc[0]
    client_info = ClientInfo(
        company_name=client_row["Название компании"],
        phone=str(client_row["Номер телефона"]),
        email=client_row["Email для связи"]
    )
    session.query(ClientInfo).delete()
    session.add(client_info)

    # Товары
    df = df.iloc[1:]
    session.query(Product).delete()
    for _, row in df.iterrows():
        company_name = row["Компания"]
        company = session.query(Company).filter_by(name=company_name).first()
        if not company:
            company = Company(name=company_name)
            session.add(company)
            session.commit()

        image_path = fetch_image(row["Название товара"])

        product = Product(
            name=row["Название товара"],
            article=row["Артикул"],
            price=row["Цена"],
            stock=row["Остаток"],
            image_path=image_path,
            buy_url=row.get("Ссылка на покупку", "http://127.0.0.1:5000/"),
            company=company
        )
        session.add(product)
    session.commit()
