import os
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


engine = create_async_engine(f'sqlite+aiosqlite:///../{os.getenv("DB_NAME")}.sqlite3', echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class AdvSql(Base):
    __tablename__ = "adv_app_advertisement"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    status: Mapped[str]
    creator_id: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


class FvsSql(Base):
    __tablename__ = "adv_app_favourites"

    id: Mapped[int] = mapped_column(primary_key=True)
    added_at: Mapped[datetime] = mapped_column(default=func.now())
    advertisement_id: Mapped[str]
    user_id: Mapped[str]


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создать все таблицы
