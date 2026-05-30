import os
import platform
import subprocess
import sys
import time

from dotenv import load_dotenv

from src.common.utils.logger import Logger
from src.daemon.services.collector import SystemCollector
from src.daemon.services.sender import MetricsSender

logger = Logger("Daemon")


def main() -> None:
    load_dotenv()
    api_host = os.getenv("DAEMON_API_HOST")

    if not api_host:
        logger.error("API_HOST is not set in environment variables!")
        sys.exit(1)

    api_key = os.getenv("DAEMON_API_KEY")

    if not api_key:
        logger.error("API_KEY is not set in environment variables!")
        sys.exit(1)

    collector = SystemCollector()
    sender = MetricsSender(api_host=api_host, api_key=api_key)
    current_os = platform.system()

    logger.info("Daemon started successfully.")

    try:
        while True:
            metrics = collector.get_system_metrics()
            commands = sender.send(metrics)

            for command in commands:
                if command == "shutdown":
                    print("Shutting down... ")
                    if current_os == "Windows":
                        subprocess.run(["shutdown", "/s", "/t", "5"])
                    else:
                        subprocess.run(["sudo", "shutdown", "-h", "now"])

                    sys.exit(0)
                elif command == "restart":
                    print("Restarting... ")
                    if current_os == "Windows":
                        subprocess.run(["shutdown", "/r", "/t", "5"])
                    else:
                        subprocess.run(["sudo", "shutdown", "-r", "now"])

                    sys.exit(0)
                elif command == "sleep":
                    print("Going to bed... ")
                    if current_os == "Windows":
                        subprocess.run(
                            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]
                        )
                    else:
                        subprocess.run(["systemctl", "suspend"])

            time.sleep(3)
    except KeyboardInterrupt:
        logger.info("Daemon is shutting down...")
    finally:
        sender.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
