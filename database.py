
from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# Папка c database.py
BASE_DIR = Path(__file__).resolve().parent

# Папка для базы данных
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Путь к файлу SQLite
DATABASE_PATH = DATA_DIR / "quotes.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(300))

    quotes = relationship("Quote", back_populates="author")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    text = Column(String(1000), nullable=False)
    category = Column(String(50), nullable=False, default="философия")
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    author = relationship("Author", back_populates="quotes")


class QuotePart(Base):
    __tablename__ = "quote_parts"

    id = Column(Integer, primary_key=True)
    text = Column(String(300), nullable=False)
    part_type = Column(String(20), nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print(f"База данных создана: {DATABASE_PATH}")
