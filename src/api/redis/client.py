from redis.asyncio import Redis
import os
from src.api.utils.logger import Logger
import sys

logger = Logger("Redis Client")

host = os.getenv("REDIS_HOST")
port = os.getenv("REDIS_PORT")

if not host or not port:
    logger.error("REDIS_HOST and REDIS_PORT are not set in environment variables!")
    sys.exit(1)

r = Redis(host=host, port=int(port), decode_responses=True)
