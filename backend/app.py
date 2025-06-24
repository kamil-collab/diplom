import io
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import pandas as pd
from backend.analyzer import generate_statistics
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Product
from backend.models.models import ClientInfo
from flask import session
from flask import make_response
from dotenv import load_dotenv
import sqlite3
from flask import request
from backend.models.models import Sale
from datetime import datetime
from flask import send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

DATABASE_URL = "sqlite:///diplom.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route("/api/client-info")
def get_client_info():
    session = Session()
    info = session.query(ClientInfo).first()
    if not info:
        return jsonify({"error": "Информация о компании не найдена"}), 404
    return jsonify({
        "company_name": info.company_name,
        "phone": info.phone,
        "email": info.email
    })

@app.route("/")
def index():
    return send_file(os.path.join(BASE_DIR, "..", "frontend", "index.html"))

@app.route("/<path:path>")
def static_files(path):
    return send_file(os.path.join(BASE_DIR, "..", "frontend", path))

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["file"]
    df = pd.read_excel(file)

    stats_df = generate_statistics(df)

    output_path = "output/statistics.xlsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stats_df.to_excel(output_path, index=False)

    return send_file(output_path, as_attachment=True)

@app.route("/api/products")
def get_products():
    session = Session()
    products = session.query(Product).all()
    data = [
        {
            "id": p.id,  # 👉 добавляем id
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "image_path": f"/static/images/{os.path.basename(p.image_path)}" if p.image_path else "",
            "company": p.company.name if p.company else ""
        } for p in products
    ]
    session.close()
    return jsonify(data)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY", "supersecret")  # добавь в .env SECRET_KEY

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    password = data.get("password")

    if password == os.getenv("ADMIN_PASSWORD"):
        session["admin"] = True
        return jsonify({"message": "OK"})
    else:
        return make_response(jsonify({"error": "Invalid password"}), 401)

@app.route("/api/check-auth")
def check_auth():
    if session.get("admin"):
        return jsonify({"authorized": True})
    return jsonify({"authorized": False}), 401
@app.route("/analyze", methods=["POST"])
def analyze_file():
    file = request.files["file"]
    df = pd.read_excel(file)

    # Пример: сохраняем в таблицу products
    conn = sqlite3.connect("data.db")
    df.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()

    # Генерация статистики, как раньше
    stats = generate_statistics(df)

    output = io.BytesIO()
    stats.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="output_stats.xlsx")

@app.route("/api/statistics")
def get_statistics():
    session = Session()
    products = session.query(Product).all()
    companies = session.query(Product.company_id).distinct().count()

    if not products:
        return jsonify({"error": "Нет данных для статистики"}), 404

    prices = [p.price for p in products]
    stocks = [p.stock for p in products]

    stats = {
        "Товаров всего": len(products),
        "Уникальных компаний": companies,
        "Средняя цена": round(sum(prices) / len(prices), 2) if prices else 0,
        "Минимальная цена": min(prices) if prices else 0,
        "Максимальная цена": max(prices) if prices else 0,
        "Суммарный остаток": sum(stocks) if stocks else 0
    }
    return jsonify(stats)

@app.route("/api/buy-cart", methods=["POST"])
def buy_cart():
    items = request.json.get("items", [])
    if not items:
        return jsonify({"error": "Корзина пуста"}), 400

    session_db = Session()
    errors = []

    for item in items:
        if "id" not in item:
            errors.append("Некорректный элемент корзины (нет id)")
            continue
        product = session_db.query(Product).filter_by(id=item["id"]).first()
        if not product:
            errors.append(f"Товар с id={item['id']} не найден")
            continue
        if product.stock < item["quantity"]:
            errors.append(f"Недостаточно {product.name}. Остаток: {product.stock}")
            continue
        product.stock -= item["quantity"]

        # 👉 фиксируем продажу
        sale = Sale(
            product_id=product.id,
            product_name=product.name,
            quantity=item["quantity"],
            price_at_sale=product.price,
            timestamp=datetime.utcnow()
        )
        session_db.add(sale)

    if errors:
        session_db.rollback()
        session_db.close()
        return jsonify({"error": " ; ".join(errors)}), 400

    session_db.commit()
    session_db.close()
    return jsonify({"message": "Покупка успешна"})

@app.route("/api/buy/<int:product_id>", methods=["POST"])
def buy_product(product_id):
    session = Session()
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        session.close()
        return jsonify({"error": "Товар не найден"}), 404
    if product.stock <= 0:
        session.close()
        return jsonify({"error": "Товар закончился"}), 400

    product.stock -= 1

    sale = Sale(
        product_id=product.id,
        product_name=product.name,
        quantity=1,
        price_at_sale=product.price,
        timestamp=datetime.utcnow()
    )
    session.add(sale)

    session.commit()
    session.close()
    return jsonify({"message": "Покупка успешна", "new_stock": product.stock})

@app.route("/api/sales")
def get_sales():
    session = Session()
    sales = session.query(Sale).all()
    result = [{
        "product_name": s.product_name,
        "quantity": s.quantity,
        "price_at_sale": s.price_at_sale,
        "timestamp": s.timestamp.isoformat()
    } for s in sales]
    session.close()
    return jsonify(result)

@app.route('/static/images/<path:filename>')
def static_images(filename):
    return send_from_directory(os.path.join(BASE_DIR, "..", "static", "images"), filename)