from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship("Product", back_populates="company")

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    article = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    description = Column(String)
    image_path = Column(String)
    buy_url = Column(String)  # 👉 новая колонка!

    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="products")

class ClientInfo(Base):
    __tablename__ = 'client_info'

    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    phone = Column(String)
    email = Column(String)

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    product_name = Column(String)
    quantity = Column(Integer)
    price_at_sale = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")