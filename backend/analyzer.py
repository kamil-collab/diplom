import pandas as pd

def generate_statistics(df: pd.DataFrame) -> pd.DataFrame:
    # Нормализация имён столбцов
    df.columns = [col.strip().lower() for col in df.columns]

    # Ожидаемые имена
    name_col = next((col for col in df.columns if "назв" in col), None)
    article_col = next((col for col in df.columns if "артикул" in col), None)
    price_col = next((col for col in df.columns if "цен" in col), None)
    stock_col = next((col for col in df.columns if "остат" in col), None)
    company_col = next((col for col in df.columns if "компан" in col), None)

    stats = {}

    # Общая информация
    stats["Всего строк (товаров)"] = len(df)
    if name_col:
        stats["Уникальных наименований"] = df[name_col].nunique()
    if article_col:
        stats["Уникальных артикулов"] = df[article_col].nunique()
    if company_col:
        stats["Уникальных компаний"] = df[company_col].nunique()

    # Цены
    if price_col:
        prices = df[price_col].dropna().astype(float)
        stats["Средняя цена"] = round(prices.mean(), 2)
        stats["Минимальная цена"] = prices.min()
        stats["Максимальная цена"] = prices.max()
        stats["Медианная цена"] = prices.median()
        stats["Товаров дешевле 100 руб."] = (prices < 100).sum()

    # Остатки
    if stock_col:
        stocks = df[stock_col].dropna().astype(int)
        stats["Суммарный остаток"] = stocks.sum()
        stats["Средний остаток"] = round(stocks.mean(), 2)
        stats["Товаров с нулевым остатком"] = (stocks == 0).sum()
        stats["Товаров с остатком < 5"] = (stocks < 5).sum()

    # Компании
    if company_col:
        top_company = df[company_col].value_counts().idxmax()
        count = df[company_col].value_counts().max()
        stats["Самая популярная компания"] = f"{top_company} ({count} товаров)"

    # Преобразуем в DataFrame
    stats_df = pd.DataFrame(list(stats.items()), columns=["Метрика", "Значение"])
    return stats_df