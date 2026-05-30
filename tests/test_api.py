import os

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"

os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "1234"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "123"
os.environ["DB_NAME"] = "db_name"

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.__main__ import app
from src.api.services.alert_service import AlertService

client = TestClient(app)


def test_post_metrics_missing_api_key() -> None:
    response = client.post("/", json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
@patch("src.api.__main__.UserRepository")
@patch("src.api.__main__.cache")
async def test_post_metrics_invalid_api_key(mock_cache, mock_repo_cls) -> None:  # type: ignore
    mock_cache.get_telegram_id_by_api_key = AsyncMock(return_value=None)

    mock_repo_instance = mock_repo_cls.return_value
    mock_repo_instance.get_by_api_key = AsyncMock(return_value=None)

    response = client.post("/", json={}, headers={"X-API-Key": "fake_key"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API Key"}


@pytest.mark.asyncio
@patch("src.api.__main__.AlertService.check_and_publish")
@patch("src.api.__main__.cache")
async def test_post_metrics_success(  # type: ignore
    mock_cache, mock_alert, valid_metrics_payload
) -> None:
    mock_cache.get_telegram_id_by_api_key = AsyncMock(return_value=123456789)

    mock_cache.set_metrics = AsyncMock()
    mock_cache.get_commands = AsyncMock(return_value=["shutdown"])
    mock_cache.clear_commands = AsyncMock()
    mock_cache.update_system_last_seen = AsyncMock()

    response = client.post(
        "/", json=valid_metrics_payload, headers={"X-API-Key": "valid_key"}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "data": {"commands": ["shutdown"]}}

    mock_alert.assert_called_once_with(123456789, 85.0)


@pytest.mark.asyncio
@patch("src.api.services.alert_service.r")
@patch("src.api.services.alert_service.cache")
async def test_alert_service_triggers_publish(mock_cache, mock_r) -> None:  # type: ignore
    mock_cache.get_user_settings = AsyncMock(
        return_value={"alert_enabled": True, "alert_temp": 80}
    )
    mock_cache.get_alert_lock = AsyncMock(return_value=False)
    mock_r.publish = AsyncMock()
    mock_cache.set_alert_lock = AsyncMock()

    await AlertService.check_and_publish(telegram_id=123, current_temp=85.0)

    mock_r.publish.assert_called_once()
    mock_cache.set_alert_lock.assert_called_once_with(
        123, AlertService.COOLDOWN_SECONDS
    )


@pytest.mark.asyncio
@patch("src.api.services.alert_service.r")
@patch("src.api.services.alert_service.cache")
async def test_alert_service_ignores_cooldown(mock_cache, mock_r) -> None:  # type: ignore
    mock_cache.get_user_settings = AsyncMock(
        return_value={"alert_enabled": True, "alert_temp": 80}
    )
    mock_cache.get_alert_lock = AsyncMock(return_value=True)
    mock_r.publish = AsyncMock()

    await AlertService.check_and_publish(telegram_id=123, current_temp=85.0)

    mock_r.publish.assert_not_called()


@pytest.mark.asyncio
@patch("src.api.services.alert_service.r")
@patch("src.api.services.alert_service.cache")
async def test_alert_service_ignores_low_temp(mock_cache, mock_r) -> None:  # type: ignore
    mock_cache.get_user_settings = AsyncMock(
        return_value={"alert_enabled": True, "alert_temp": 80}
    )
    mock_r.publish = AsyncMock()

    await AlertService.check_and_publish(telegram_id=123, current_temp=70.0)

    mock_r.publish.assert_not_called()
