from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot_localhost_async.models_alchemy import AdvSql, FvsSql


async def orm_get_all_open_advertisements(session: AsyncSession):
    """
    Получить все открытые объявления
    """
    query = select(AdvSql).where(AdvSql.status == "OPEN").order_by(desc(AdvSql.id))
    res = await session.execute(query)
    return res.scalars().all()


async def orm_get_user_advertisements(session: AsyncSession, user_id: int):
    """
    Получить все объявления конкретного пользователя
    """
    query = select(AdvSql).where(AdvSql.creator_id == user_id).order_by(desc(AdvSql.id))
    res = await session.execute(query)
    return res.scalars().all()


async def orm_get_advertisement_by_id(session: AsyncSession, adv_id: int):
    """
    Получить объявление по его id
    """
    query = select(AdvSql).where(AdvSql.id == adv_id)
    res = await session.execute(query)
    return res.scalar()


async def orm_get_user_drafts(session: AsyncSession, user_id: int):
    """
    Получить все черновики конкретного пользователя
    """
    query = (
        select(AdvSql)
        .where((AdvSql.creator_id == user_id) & (AdvSql.status == "DRAFT"))
        .order_by(desc(AdvSql.id))
    )
    res = await session.execute(query)
    return res.scalars().all()


async def orm_get_user_favourites(session: AsyncSession, ids_list: list):
    """
    Получить все избранные объявления конкретного пользователя
    """
    fvs_ids = [i.advertisement.id for i in ids_list]
    query = select(AdvSql).where(AdvSql.id.in_(fvs_ids)).order_by(desc(AdvSql.id))
    res = await session.execute(query)
    return res.scalars().all()


async def orm_delete_advertisement(session: AsyncSession, id_for_delete: int, user_id: int):
    """
    Удалить объявление пользователя по id
    """
    query = delete(AdvSql).where((AdvSql.id == id_for_delete) & (AdvSql.creator_id == user_id))
    await session.execute(query)
    await session.commit()


async def orm_delete_from_favourites(session: AsyncSession, id_for_delete: int, user_id: int):
    """
    Удалить объявление из своего Избранного
    """
    query = delete(FvsSql).where(
        (FvsSql.advertisement_id == id_for_delete) & (FvsSql.user_id == user_id)
    )
    await session.execute(query)
    await session.commit()


async def orm_search_in_advertisements(session: AsyncSession, data: dict):
    """
    Фильтр объявлений по совпадению в названии или описании
    """
    query = (
        select(AdvSql)
        .where(
            (AdvSql.title.contains(data["search_param"])) |
            (AdvSql.description.contains(data["search_param"]))
        )
        .where(AdvSql.status == "OPEN")
        .order_by(desc(AdvSql.id))
    )
    res = await session.execute(query)
    return res.scalars().all()
