from pydantic import BaseModel


class Metrics(BaseModel):
    cpu: dict[str, float | list[float] | dict[str, float] | int]
    memory: dict[str, dict[str, float]]
    disks: dict[str, dict[str, float]]
    network: dict[str, float]
    processes: dict[str, int]
