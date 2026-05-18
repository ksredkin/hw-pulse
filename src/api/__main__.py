import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.models.models import Metrics
from src.common.services.cache import cache
from src.common.utils.logger import Logger

logger = Logger("Api")
app = FastAPI()


@app.post("/")
async def post_metrics(metrics: Metrics) -> JSONResponse:
    await cache.set_metrics(metrics.model_dump())
    commands = await cache.get_commands() or []
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
