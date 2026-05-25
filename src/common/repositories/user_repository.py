from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, telegram_id: int, api_key: str) -> User:
        user = User(telegram_id=telegram_id, api_key=api_key)
        self.session.add(user)
        await self.session.refresh(user)
        return user

    async def get_by_tg_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_api_key(self, api_key: str) -> User | None:
        result = await self.session.execute(select(User).where(User.api_key == api_key))
        return result.scalar_one_or_none()
