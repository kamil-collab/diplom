from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Product, Sale
from datetime import datetime
import asyncio
import os

BOT_TOKEN = "7855635475:AAEeAtmkgPhQbi8PcsDUA5Pw4pbyJBT1RUQ"
CHAT_ID = "7727164310"
SHOP_URL = "https://diplom-8o5u.onrender.com/"

DATABASE_URL = "sqlite:///diplom.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать!\n\n"
        "📊 /statistics — Панель статистики\n"
        "💰 /sales — Продажи"
    )

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    products = session.query(Product).all()
    session.close()

    if not products:
        await update.message.reply_text("Нет данных о товарах.")
        return

    companies = len(set(p.company_id for p in products if p.company_id))
    prices = [p.price for p in products]
    stocks = [p.stock for p in products]

    msg = (
        f"📦 Товаров всего: {len(products)}\n"
        f"🏢 Уникальных компаний: {companies}\n"
        f"💵 Средняя цена: {round(sum(prices) / len(prices), 2)} ₽\n"
        f"⬇️ Мин. цена: {min(prices)} ₽\n"
        f"⬆️ Макс. цена: {max(prices)} ₽\n"
        f"📦 Суммарный остаток: {sum(stocks)}"
    )
    await update.message.reply_text(msg)

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    sales = session.query(Sale).order_by(Sale.timestamp.desc()).limit(10).all()
    session.close()

    if not sales:
        await update.message.reply_text("Нет данных о продажах.")
        return

    msg = "\n".join(
        f"{s.product_name} — {s.quantity} шт. по {s.price_at_sale}₽ ({s.timestamp.strftime('%d.%m.%Y %H:%M')})"
        for s in sales
    )
    await update.message.reply_text("🧾 Последние продажи:\n\n" + msg)

async def check_low_stock(app):
    while True:
        session = Session()
        low_stock_products = session.query(Product).filter(Product.stock <= 5).all()
        session.close()

        for p in low_stock_products:
            message = (
                f"⚠️ Товар {p.name} заканчивается!\n"
                f"Остаток: {p.stock} шт.\n"
                f"💳 Купить: {SHOP_URL}"
            )
            try:
                await app.bot.send_message(chat_id=CHAT_ID, text=message)
            except Exception as e:
                print("Ошибка при отправке уведомления:", e)

        await asyncio.sleep(15)  # каждые 15 сек

async def main():
    print("Бот запущен")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("statistics", statistics))
    app.add_handler(CommandHandler("sales", sales))
    asyncio.create_task(check_low_stock(app))

    await app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
