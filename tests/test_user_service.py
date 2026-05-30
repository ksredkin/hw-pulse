import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.bot.services.user import UserService
from src.common.database.models import User
from src.common.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_and_get_user(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> None:
    async with sessionmaker() as session:
        repository = UserRepository(session)
        service = UserService(repository)

        telegram_id = 123456

        new_user = await service.create_user(telegram_id)
        assert isinstance(new_user, User)
        assert new_user.telegram_id == telegram_id

        getted_user = await repository.get_by_tg_id(telegram_id)
        assert getted_user == new_user
