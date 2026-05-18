from fastapi import FastAPI
from src.api.utils.logger import Logger
import uvicorn
import os
import sys
from src.api.models.models import Metrics
from src.api.services.cache import cache
from dotenv import load_dotenv

logger = Logger("Api")
app = FastAPI()


@app.post("/")
async def post_metrics(metrics: Metrics) -> list[str]:
    await cache.set_metrics(metrics)
    commands = await cache.get_commands()
    logger.info(str(metrics))
    logger.info(commands)
    return commands if commands else []


def main() -> None:
    host = os.getenv("API_HOST")
    port = os.getenv("API_PORT")

    if not host or not port:
        logger.error("API_HOST and API_PORT are not set in environment variables!")
        sys.exit(1)

    uvicorn.run(app, host=host, port=int(port))

if __name__ == "__main__":
    main()
