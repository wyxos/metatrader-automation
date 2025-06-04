import os
from unittest.mock import MagicMock

import MetaTrader5 as mt5


def initialize_and_login():
    """Initialize MT5 terminal and perform a login."""
    mt5_path = os.getenv('MT5_PATH', 'C:/Program Files/MetaTrader 5/terminal64.exe')
    mt5_path = mt5_path.replace('\\', '/')

    if not mt5.initialize(path=mt5_path):
        return False

    login_id = 999999
    password = "abcdef"
    server = "xyz-Demo"

    if not mt5.login(login=login_id, password=password, server=server):
        return False

    mt5.terminal_info()
    mt5.version()
    mt5.shutdown()
    return True


def test_initialize_and_login(monkeypatch):
    """Verify that MetaTrader5 initialization and login are attempted."""
    initialize_mock = MagicMock(return_value=True)
    login_mock = MagicMock(return_value=True)
    terminal_info_mock = MagicMock()
    version_mock = MagicMock()
    shutdown_mock = MagicMock()

    monkeypatch.setattr(mt5, "initialize", initialize_mock)
    monkeypatch.setattr(mt5, "login", login_mock)
    monkeypatch.setattr(mt5, "terminal_info", terminal_info_mock)
    monkeypatch.setattr(mt5, "version", version_mock)
    monkeypatch.setattr(mt5, "shutdown", shutdown_mock)

    assert initialize_and_login() is True

    expected_path = os.getenv('MT5_PATH', 'C:/Program Files/MetaTrader 5/terminal64.exe').replace('\\', '/')
    initialize_mock.assert_called_once_with(path=expected_path)
    login_mock.assert_called_once_with(login=999999, password="abcdef", server="xyz-Demo")
    terminal_info_mock.assert_called_once()
    version_mock.assert_called_once()
    shutdown_mock.assert_called_once()
