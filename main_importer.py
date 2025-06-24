from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base, Product
from backend.logic.importer import import_products_from_excel

DATABASE_URL = "sqlite:///diplom.db"

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

# Создание таблиц, если их ещё нет
Base.metadata.create_all(engine)

def run_import(file_path: str):
    session = Session()
    session.query(Product).delete()  # Очистка старых записей
    import_products_from_excel(file_path, session)
    print("Импорт завершён")

if __name__ == "__main__":
    run_import("uploads/catalog.xlsx")