import os
import sys
import time

from dotenv import load_dotenv

from src.daemon.services.collector import SystemCollector
from src.daemon.services.sender import MetricsSender
from src.daemon.utils.logger import Logger

logger = Logger("Daemon")


def main() -> None:
    load_dotenv()
    api_host = os.getenv("API_HOST")

    if not api_host:
        logger.error("API_HOST is not set in environment variables!")
        sys.exit(1)

    collector = SystemCollector()
    sender = MetricsSender(api_host=api_host)

    logger.info("Daemon started successfully.")

    try:
        while True:
            metrics = collector.get_system_metrics()
            commands = sender.send(metrics)

            for command in commands:
                if command == "kukareky":
                    print("Kukareky! 🐓")

            time.sleep(3)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        sender.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
