import pytest

from src.common.repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.common.database.models import User


@pytest.mark.asyncio
async def test_create_and_get_user(sessionmaker: async_sessionmaker) -> None:
    async with sessionmaker() as session:
        repository = UserRepository(session)

        telegram_id = 123456
        api_key = "12345-abcde-fghij-klmno-pqrst-uvwxy-z6789"

        created_user = await repository.create(telegram_id, api_key)
        assert isinstance(created_user, User)
        assert created_user.telegram_id == telegram_id
        assert created_user.api_key == api_key

        user_getted_by_tg_id = await repository.get_by_tg_id(telegram_id)
        assert isinstance(user_getted_by_tg_id, User)
        assert user_getted_by_tg_id.telegram_id == telegram_id
        assert user_getted_by_tg_id.api_key == api_key
        assert user_getted_by_tg_id.id == created_user.id
        assert user_getted_by_tg_id.alert_enabled == created_user.alert_enabled
        assert user_getted_by_tg_id.alert_temp == created_user.alert_temp

        user_getted_by_api_key = await repository.get_by_api_key(api_key)
        assert isinstance(user_getted_by_api_key, User)
        assert user_getted_by_api_key.telegram_id == telegram_id
        assert user_getted_by_api_key.api_key == api_key
        assert user_getted_by_api_key.id == created_user.id
        assert user_getted_by_api_key.alert_enabled == created_user.alert_enabled
        assert user_getted_by_api_key.alert_temp == created_user.alert_temp


@pytest.mark.asyncio
async def test_update_user_settings(sessionmaker: async_sessionmaker) -> None:
    async with sessionmaker() as session:
        repository = UserRepository(session)

        telegram_id = 123456
        api_key = "12345-abcde-fghij-klmno-pqrst-uvwxy-z6789"
        new_alert_enabled = False
        new_alert_temp = 40

        none_user = await repository.get_by_tg_id(telegram_id)
        assert none_user is None

        created_user = await repository.create(telegram_id, api_key)
        assert isinstance(created_user, User)
        assert created_user.telegram_id == telegram_id
        assert created_user.api_key == api_key
        
        await repository.update_settings_by_tg_id(telegram_id, new_alert_enabled, new_alert_temp)

        user_with_new_settings = await repository.get_by_tg_id(telegram_id)
        assert user_with_new_settings.alert_enabled == new_alert_enabled
        assert user_with_new_settings.alert_temp == new_alert_temp
