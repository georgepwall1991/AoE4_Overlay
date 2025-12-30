import sys
import os
import unittest
import tempfile
from unittest.mock import MagicMock, patch

# Clear any cached modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay' or mod_name.startswith('PyQt5'):
        del sys.modules[mod_name]

# Mock dependencies
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mock_pyqt import setup_pyqt_mocks
setup_pyqt_mocks()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock other modules that are hard to test
sys.modules['keyboard'] = MagicMock()
sys.modules['appdirs'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock
sys.modules['requests'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()

# Mock websockets with submodules
websockets_mock = MagicMock()
websockets_legacy_mock = MagicMock()
websockets_legacy_server_mock = MagicMock()
websockets_mock.legacy = websockets_legacy_mock
websockets_legacy_mock.server = websockets_legacy_server_mock
sys.modules['websockets'] = websockets_mock
sys.modules['websockets.legacy'] = websockets_legacy_mock
sys.modules['websockets.legacy.server'] = websockets_legacy_server_mock

import overlay.tab_main as tab_main_module
from overlay.tab_main import TabWidget


class TestTabMain(unittest.TestCase):

    @patch('overlay.tab_main.Websocket_manager')
    @patch('overlay.tab_main.Api_checker')
    @patch('overlay.tab_main.MatchHistoryTab')
    @patch('overlay.tab_main.RandomTab')
    @patch('overlay.tab_main.BoTab')
    @patch('overlay.tab_main.OverrideTab')
    @patch('overlay.tab_main.SettingsTab')
    def test_tab_widget_init(self, mock_settings_tab, mock_override_tab,
                              mock_bo_tab, mock_random_tab, mock_games_tab,
                              mock_api, mock_ws):
        # Setup mock returns
        mock_override_tab.return_value = MagicMock()
        mock_override_tab.return_value.data_override = MagicMock()
        mock_override_tab.return_value.update_override = MagicMock()
        mock_settings_tab.return_value = MagicMock()
        mock_settings_tab.return_value.new_profile = MagicMock()

        parent = MagicMock()
        tab_widget = TabWidget(parent, "1.0.0")

        self.assertEqual(tab_widget.version, "1.0.0")
        self.assertFalse(tab_widget.force_stop)

    @patch('overlay.tab_main.Websocket_manager')
    @patch('overlay.tab_main.Api_checker')
    @patch('overlay.tab_main.MatchHistoryTab')
    @patch('overlay.tab_main.RandomTab')
    @patch('overlay.tab_main.BoTab')
    @patch('overlay.tab_main.OverrideTab')
    @patch('overlay.tab_main.SettingsTab')
    def test_stop_checking_api(self, mock_settings_tab,
                                mock_override_tab, mock_bo_tab, mock_random_tab,
                                mock_games_tab, mock_api, mock_ws):
        # Setup mock returns
        mock_override_tab.return_value = MagicMock()
        mock_override_tab.return_value.data_override = MagicMock()
        mock_override_tab.return_value.update_override = MagicMock()
        mock_settings_tab.return_value = MagicMock()
        mock_settings_tab.return_value.new_profile = MagicMock()

        tab_widget = TabWidget(MagicMock(), "1.0.0")
        tab_widget.api_checker = MagicMock()

        # Patch close_session directly on the module to avoid discover mode issues
        mock_close_session = MagicMock()
        original_close_session = tab_main_module.close_session
        tab_main_module.close_session = mock_close_session

        try:
            tab_widget.stop_checking_api()

            self.assertTrue(tab_widget.force_stop)
            self.assertTrue(tab_widget.api_checker.force_stop)
            mock_close_session.assert_called_once()
        finally:
            tab_main_module.close_session = original_close_session

    @patch('overlay.tab_main.Websocket_manager')
    @patch('overlay.tab_main.Api_checker')
    @patch('overlay.tab_main.MatchHistoryTab')
    @patch('overlay.tab_main.RandomTab')
    @patch('overlay.tab_main.BoTab')
    @patch('overlay.tab_main.OverrideTab')
    @patch('overlay.tab_main.SettingsTab')
    def test_override_update_event(self, mock_settings_tab, mock_override_tab,
                                    mock_bo_tab, mock_random_tab, mock_games_tab,
                                    mock_api, mock_ws):
        # Setup mock returns
        mock_override_tab.return_value = MagicMock()
        mock_override_tab.return_value.data_override = MagicMock()
        mock_override_tab.return_value.update_override = MagicMock()
        mock_settings_tab.return_value = MagicMock()
        mock_settings_tab.return_value.new_profile = MagicMock()

        tab_widget = TabWidget(MagicMock(), "1.0.0")

        tab_widget.override_update_event(True)
        self.assertTrue(tab_widget.prevent_overlay_update)

        tab_widget.override_update_event(False)
        self.assertFalse(tab_widget.prevent_overlay_update)


if __name__ == '__main__':
    unittest.main()
