from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Product, Sale
import asyncio
import os

DATABASE_URL = "sqlite:///diplom.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

BOT_TOKEN = "7441242871:AAFHviTnyTP1J5dgW26lgQtzSicwN-PQtaY"
SHOP_URL = "http://127.0.0.1:5000/"  # или ссылка из Excel, если решим так

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добро пожаловать! Доступные команды:\n/statistics — Панель статистики\n/sales — Продажи")

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    products = session.query(Product).all()
    if not products:
        await update.message.reply_text("Нет данных о товарах.")
        session.close()
        return

    companies = len(set(p.company_id for p in products if p.company_id))
    prices = [p.price for p in products]
    stocks = [p.stock for p in products]

    msg = (
        f"Товаров всего: {len(products)}\n"
        f"Уникальных компаний: {companies}\n"
        f"Средняя цена: {round(sum(prices) / len(prices), 2) if prices else 0}\n"
        f"Минимальная цена: {min(prices) if prices else 0}\n"
        f"Максимальная цена: {max(prices) if prices else 0}\n"
        f"Суммарный остаток: {sum(stocks) if stocks else 0}"
    )
    await update.message.reply_text(msg)
    session.close()

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    sales = session.query(Sale).all()
    if not sales:
        await update.message.reply_text("Нет данных о продажах.")
        session.close()
        return

    msg = "\n".join(
        f"{s.product_name} — {s.quantity} шт. по {s.price_at_sale} руб. {s.timestamp.strftime('%d.%m.%Y %H:%M')}"
        for s in sales[-10:]  # последние 10 продаж
    )
    await update.message.reply_text(msg)
    session.close()

async def check_low_stock(app):
    while True:
        session = Session()
        low_stock_products = session.query(Product).filter(Product.stock <= 5).all()
        session.close()
        if low_stock_products:
            for p in low_stock_products:
                text = (
                    f"⚠️ Товар {p.name} заканчивается!\n"
                    f"Остаток: {p.stock}\n"
                    f"Пополнить можно здесь: {p.buy_url or SHOP_URL}"
                )
                await app.bot.send_message(chat_id="868819144", text=text)

        await asyncio.sleep(15)  # каждые 30 минут

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("statistics", statistics))
    app.add_handler(CommandHandler("sales", sales))

    # Запускаем проверку на остатки
    asyncio.create_task(check_low_stock(app))

    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()