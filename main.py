from backend.app import app
from backend.models.models import Base
from sqlalchemy import create_engine
import os

DATABASE_URL = "sqlite:///diplom.db"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)