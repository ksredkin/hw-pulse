import platform

import httpx
import psutil


class SystemCollector:
    def _get_cpu_metrics(self) -> dict[str, float]:
        cpu_freq = psutil.cpu_freq()
        return {
            "percent": psutil.cpu_percent(interval=None),
            "percent_per_core": psutil.cpu_percent(interval=None, percpu=True),
            "cores": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "frequency": {
                "current": cpu_freq.current if cpu_freq else 0,
                "min": cpu_freq.min if cpu_freq else 0,
                "max": cpu_freq.max if cpu_freq else 0,
            },
            "temperature": self._get_cpu_temperature(),
        }

    def _get_memory_metrics(self) -> dict[str, dict[str, float]]:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "ram": {
                "percent": mem.percent,
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
            },
            "swap": {"percent": swap.percent},
        }

    def _get_disk_metrics(self) -> dict[str, dict[str, float]]:
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.mountpoint] = {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "usage_percent": usage.percent,
                }
            except PermissionError:
                continue
        return disk_info

    def _get_windows_cpu_temperature(self) -> float | None:
        try:
            url = "http://127.0.0.1:8085/data.json"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Connection": "close",
            }

            response = httpx.get(url, headers=headers, timeout=5.0)
            response.raise_for_status()

            data = response.json()

            def find_cpu_temp(node: dict) -> float | None:  # type: ignore
                if node.get("Text") == "Temperatures":
                    for child in node.get("Children", []):
                        name = child.get("Text", "")
                        if any(
                            k in name
                            for k in ("CPU Package", "Core Average", "Core (Tctl/Tdie)")
                        ):
                            val_str = (
                                child.get("Value", "")
                                .replace(" °C", "")
                                .replace(",", ".")
                            )
                            try:
                                return float(val_str)
                            except ValueError:
                                pass

                for child in node.get("Children", []):
                    result = find_cpu_temp(child)
                    if result is not None:
                        return result
                return None

            return find_cpu_temp(data)

        except Exception:
            pass

        return None

    def _get_cpu_temperature(self) -> float | None:
        current_os = platform.system()

        if current_os == "Linux":
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                return round(temps["coretemp"][0].current, 1)  # type: ignore
            elif temps:
                first_key = list(temps.keys())[0]
                return round(temps[first_key][0].current, 1)  # type: ignore

        elif current_os == "Windows":
            return self._get_windows_cpu_temperature()

        return None

    def get_system_metrics(
        self,
    ) -> dict[
        str,
        dict[str, float | list[float] | dict[str, float]]
        | dict[str, dict[str, float]]
        | dict[str, float]
        | dict[str, int],
    ]:
        net_io = psutil.net_io_counters()
        return {
            "cpu": self._get_cpu_metrics(),
            "memory": self._get_memory_metrics(),
            "disks": self._get_disk_metrics(),
            "network": {
                "read_mb": round(net_io.bytes_recv / (1024**2), 2),
                "write_mb": round(net_io.bytes_sent / (1024**2), 2),
            },
            "processes": {"count": len(psutil.pids())},
        }
