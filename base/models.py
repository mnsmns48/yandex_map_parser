from typing import Optional

from sqlalchemy.dialects.postgresql import JSONB, JSON
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Rubrikator(Base):
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]


class ScrapeData(Base):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    category: Mapped[Optional[str]]
    region: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    name: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    phone: Mapped[Optional[str]]
    rank: Mapped[Optional[float]]
    rank_grade: Mapped[Optional[int]]
    link: Mapped[Optional[str]]
    site: Mapped[Optional[str]] = mapped_column(unique=True)
    showcase: Mapped[Optional[dict]] = mapped_column(type_=JSON)
    vkontakte: Mapped[Optional[str]]
    ok: Mapped[Optional[str]]
    telegram: Mapped[Optional[str]]
    whatsapp: Mapped[Optional[str]]
    viber: Mapped[Optional[str]]
    youtube: Mapped[Optional[str]]
