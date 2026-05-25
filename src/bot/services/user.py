import secrets

from src.common.database.models import User
from src.common.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    async def create_user(self, telegram_id: int) -> User | None:
        existing_user = await self.repo.get_by_tg_id(telegram_id)

        if existing_user:
            return None

        new_api_key = secrets.token_urlsafe(32)
        new_user = await self.repo.create(telegram_id, new_api_key)
        return new_user
