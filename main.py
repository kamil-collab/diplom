from backend.app import app
from backend.models.models import Base
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///diplom.db"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

if __name__ == "__main__":
    app.run(debug=True)
