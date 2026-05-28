import os
import sys

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader

from src.api.schemas.metrics import Metrics
from src.api.services.alert_service import AlertService
from src.common.database.connection import get_db_session
from src.common.repositories.user_repository import UserRepository
from src.common.services.cache import cache
from src.common.utils.logger import Logger

logger = Logger("Api")
app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_current_user_tg_id(api_key: str = Security(api_key_header)) -> int:
    cached_tg_id = await cache.get_telegram_id_by_api_key(api_key)
    if cached_tg_id:
        return int(cached_tg_id)

    async with get_db_session() as session:  # type: ignore
        repository = UserRepository(session)
        user = await repository.get_by_api_key(api_key)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        cache.set_telegram_id_by_api_key(api_key, user.telegram_id)  # type: ignore
        return user.telegram_id  # type: ignore


@app.post("/")
async def post_metrics(
    metrics: Metrics,
    background_tasks: BackgroundTasks,
    telegram_id: int = Depends(get_current_user_tg_id),
) -> JSONResponse:
    await cache.set_metrics(metrics.model_dump(), telegram_id)
    commands = await cache.get_commands(telegram_id) or []
    background_tasks.add_task(
        AlertService.check_and_publish,
        telegram_id,
        metrics.cpu["temperature"],  # type: ignore
    )
    return JSONResponse(
        {"status": "success", "data": {"commands": commands}}, status_code=200
    )


def main() -> None:
    host = os.getenv("API_HOST")
    port = os.getenv("API_PORT")

    if not host or not port:
        logger.error("API_HOST and API_PORT are not set in environment variables!")
        sys.exit(1)

    uvicorn.run(app, host=host, port=int(port))


if __name__ == "__main__":
    main()
