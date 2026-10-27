from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import History, User


async def get_or_create_user(session: AsyncSession, vk_id: int) -> User:
    result = await session.execute(select(User).where(User.vk_id == vk_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(vk_id=vk_id)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def set_user_city(session: AsyncSession, vk_id: int, city: str) -> None:
    user = await get_or_create_user(session, vk_id)
    user.city = city
    await session.commit()


async def get_user_city(session: AsyncSession, vk_id: int) -> str | None:
    user = await get_or_create_user(session, vk_id)
    return user.city


async def add_history(
    session: AsyncSession, vk_id: int, query: str, response: str
) -> None:
    user = await get_or_create_user(session, vk_id)
    session.add(History(user_id=user.id, query=query, response=response))
    await session.commit()


async def get_recent_history(
    session: AsyncSession, vk_id: int, limit: int = 5
) -> list[History]:
    user = await get_or_create_user(session, vk_id)
    result = await session.execute(
        select(History)
        .where(History.user_id == user.id)
        .order_by(desc(History.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recent_cities(
    session: AsyncSession, vk_id: int, limit: int = 3
) -> list[str]:
    """Возвращает список последних уникальных городов пользователя."""
    user = await get_or_create_user(session, vk_id)
    result = await session.execute(
        select(History.query)
        .where(History.user_id == user.id)
        .order_by(desc(History.created_at))
        .limit(limit * 3)  # берём с запасом, чтобы было из чего выбирать
    )
    
    queries = list(result.scalars().all())
    unique_cities = []
    for q in queries:
        if q not in unique_cities and len(unique_cities) < limit:
            unique_cities.append(q)
    return unique_cities