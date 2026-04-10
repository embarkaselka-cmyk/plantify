from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    articles: Mapped[list["Article"]] = relationship(back_populates="author", cascade="all, delete-orphan")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped[Optional[User]] = relationship(back_populates="articles")


class Magazine(Base):
    __tablename__ = "magazines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_number: Mapped[str] = mapped_column(String(100), default="1")
    primary_color: Mapped[str] = mapped_column(String(20), default="#2563eb")
    secondary_color: Mapped[str] = mapped_column(String(20), default="#0f172a")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    layout_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None


class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True


class ArticleGenerateRequest(BaseModel):
    author_name: str
    title: str
    topic: str
    category: str
    mode: Literal["online", "offline", "auto"] = "auto"


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None


class ArticleOut(BaseModel):
    id: int
    author_name: str
    title: str
    topic: str
    category: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MagazineCreate(BaseModel):
    name: str
    issue_number: str = "1"
    primary_color: str = "#2563eb"
    secondary_color: str = "#0f172a"
    logo_url: Optional[str] = None
    article_ids: list[int] = []


class MagazineOut(BaseModel):
    id: int
    name: str
    issue_number: str
    primary_color: str
    secondary_color: str
    logo_url: Optional[str]
    layout_json: str
    created_at: datetime

    class Config:
        from_attributes = True
