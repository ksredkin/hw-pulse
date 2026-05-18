import httpx

from src.common.utils.logger import Logger

logger = Logger("MetricsSender")


class MetricsSender:
    def __init__(self, api_host: str):
        self.api_host = api_host
        self.client = httpx.Client()

    def send(
        self,
        metrics_data: dict[
            str,
            dict[str, float | list[float] | dict[str, float]]
            | dict[str, dict[str, float]]
            | dict[str, float]
            | dict[str, int],
        ],
    ) -> list[str]:
        try:
            response = self.client.post(self.api_host, json=metrics_data)

            if response.status_code != 200:
                logger.warning(f"Server returned status code {response.status_code}")
                return []

            response_json = response.json()
            data = response_json.get("data")

            if not isinstance(data, dict):
                logger.warning("Incorrect response data")
                return []

            commands = data.get("commands")

            if not isinstance(commands, list):
                logger.warning('Expected "commands" to be a list')
                return []

            return commands
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to server: {e}")
            return []
        except Exception as e:
            logger.info(f"Error occured: {e}")
            return []

    def close(self) -> None:
        self.client.close()
