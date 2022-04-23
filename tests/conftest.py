import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    from door_service.daemon import create_app

    queue = MagicMock()
    yield TestClient(create_app(queue))


@pytest.fixture()
def mock_rpi():
    mock_rpi, mock_pirc, mock_ada = MagicMock(), MagicMock(), MagicMock()
    modules = {
        **sys.modules,
        "RPi": mock_rpi,
        "RPi.GPIO": mock_rpi.GPIO,
        "pirc522": mock_pirc,
        "Adafruit_CharLCD": mock_ada,
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    return mock_rpi, mock_pirc, mock_ada
