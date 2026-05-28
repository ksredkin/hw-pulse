from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    api_key = Column(String, unique=True)
    alert_enabled = Column(Boolean, default=True)
    alert_temp = Column(Integer, default=80)
