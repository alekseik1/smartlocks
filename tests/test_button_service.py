from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize(
    "press_count",
    [1, 2, 3, 8, 11],
)
def test_button_pressed_correct(mock_rpi, mocker, press_count):
    mock_rpi, _, _ = mock_rpi
    edge_mock = MagicMock()
    # hack to exit infinite loop on second iteration
    edge_mock.side_effect = [None] * press_count + [KeyboardInterrupt()]
    mock_rpi.GPIO.wait_for_edge = edge_mock
    # GIVEN mocked RPI
    from button_service.daemon import CONTROL_PORT, main

    mock = MagicMock()
    with mocker.patch("requests.get", mock):
        # WHEN main is called
        with pytest.raises(KeyboardInterrupt):
            main()
        # THEN unlock and lock requests are made
        # 2 per each press
        assert mock.call_count == 2 * press_count
        # each even is unlock and odd is lock
        for i in range(0, 2 * press_count, 2):
            assert mock.call_args_list[i][0] == (
                f"http://localhost:{CONTROL_PORT}/unlock",
            )
            assert mock.call_args_list[i + 1][0] == (
                f"http://localhost:{CONTROL_PORT}/lock",
            )
