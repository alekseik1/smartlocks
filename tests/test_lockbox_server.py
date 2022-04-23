import sys
from multiprocessing import Queue
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


@pytest.mark.parametrize("action,value", [("unlock", 1), ("lock", 0)])
def test_put_correct_value_on_endpoint_call(client, action, value):
    # GIVEN app with action endpoint
    # WHEN endpoint is called
    client.get(f"/{action}")
    # THEN correct value is put into queue
    client.app.queue.put.assert_called()
    assert client.app.queue.put.call_args[0] == (value,)


def test_health_check_correct(client):
    # GIVEN app with health check endpoint
    # WHEN health check endpoint is called
    r = client.get(f"/health_check")
    # THEN status code is 200
    assert r.status_code == 200


def test_health_check_crashed(client):
    # GIVEN app with health check endpoint with crashed queue
    # WHEN health check endpoint is called
    client.app.queue.put.side_effect = ValueError("hello")
    r = client.get(f"/health_check")
    # THEN status code is 400
    assert r.status_code == 400


@pytest.mark.parametrize("value, method", ((1, "open"), (0, "close")))
def test_can_handle_single_item_queue(mock_rpi, mocker, value, method):
    # GIVEN mocker RPi API
    # GIVEN queue with ONE item
    queue = Queue()
    queue.put(value)
    mock = MagicMock()
    # GIVEN hack to exit after one item is handled
    getattr(mock.return_value, method).side_effect = [KeyboardInterrupt()]
    with mocker.patch("device_manager.DoorMagnet", mock):
        from door_service.daemon import handle_queue

        with pytest.raises(KeyboardInterrupt):
            # WHEN handle_queue meets a new item
            handle_queue(queue)
        # THEN method (open or close) is called
        getattr(mock.return_value, method).assert_called_once()


@pytest.mark.parametrize(
    "value_list", ([0, 1, 0, 1], [0, 0, 0, 1, 1, 0], [0, 1, 1, 1, 0, 0, 1, 0, 0, 1])
)
def test_queue_can_handle_multiple_items(mock_rpi, mocker, value_list):
    # GIVEN mocker RPi API
    mock = MagicMock()
    queue = Queue()
    # GIVEN queue with SOME items
    expected_calls = {0: 0, 1: 0}
    # side effects
    sfs = {1: [], 0: []}
    for one_value in value_list:
        queue.put(one_value)
        sfs[one_value].append(None)
        expected_calls[one_value] += 1
    # the last side effect of the last item MUST be KeyboardInterrupt, or else infinite loop never ends
    sfs[one_value][-1] = KeyboardInterrupt()
    mock.return_value.open.side_effect = sfs[1]
    mock.return_value.close.side_effect = sfs[0]

    # GIVEN hack to exit after one item is handled
    with mocker.patch("device_manager.DoorMagnet", mock):
        # Remove delays :)
        with mocker.patch("door_service.daemon.OPEN_TIME", MagicMock(return_value=0)):
            with mocker.patch("time.sleep", MagicMock()):
                from door_service.daemon import handle_queue

                with pytest.raises(KeyboardInterrupt):
                    # WHEN handle_queue meets a new item
                    handle_queue(queue)
    # THEN method (open or close) is called correct number of times
    assert mock.return_value.open.call_count == expected_calls[1]
    assert mock.return_value.close.call_count == expected_calls[0]
