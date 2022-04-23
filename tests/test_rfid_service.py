from unittest.mock import MagicMock

import pytest

from door_service.daemon import CONTROL_PORT


def test_rfid_okay(mock_rpi, mocker):
    card_mock = MagicMock()
    card_mock.return_value.wait_card.return_value = (None, [5, 5, 5, 5])
    acl_mock = MagicMock(return_value=False)
    fpmi_mock = MagicMock(return_value=(True, "admin"))
    r_mock = MagicMock(side_effect=[KeyboardInterrupt()])
    with mocker.patch("device_manager.RfidReader", card_mock):
        with mocker.patch("rfid_service.daemon.hardcoded_allowed_to_unlock", acl_mock):
            with mocker.patch("rfid_service.daemon.fpmi_allowed_to_unlock", fpmi_mock):
                with mocker.patch("requests.get", r_mock):
                    from rfid_service.daemon import main

                    with pytest.raises(KeyboardInterrupt):
                        main()
    r_mock.assert_called()
    assert r_mock.call_args[0] == (f"http://localhost:{CONTROL_PORT}/unlock",)


def test_hardcoded_list(mock_rpi):
    from rfid_service.daemon import hardcoded_allowed_to_unlock

    hardcoded_allowed_to_unlock("2.2.2.2")
