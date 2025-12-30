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

sys.modules['appdirs'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock
sys.modules['keyboard'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.tab_override import OverrideTab


class TestTabOverride(unittest.TestCase):

    def test_override_tab_init(self):
        with patch('overlay.tab_override.settings') as mock_settings:
            mock_settings.team_colors = [(0, 0, 0, 0)]
            mock_settings.civ_stats_color = "#000000"
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12

            tab = OverrideTab(MagicMock())

            # Check that the tab has the expected attributes
            self.assertTrue(hasattr(tab, 'overlay_widget'))
            self.assertTrue(hasattr(tab, 'live_data'))
            self.assertTrue(hasattr(tab, 'changed_data'))

    def test_update_data(self):
        with patch('overlay.tab_override.settings') as mock_settings:
            mock_settings.team_colors = [(0, 0, 0, 0)]
            mock_settings.civ_stats_color = "#000000"
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12

            tab = OverrideTab(MagicMock())
            tab.prevent_ck.setChecked(False)

            player_data = {
                'map': 'Test Map',
                'players': []
            }

            # Mock overlay_widget.update_data
            tab.overlay_widget.update_data = MagicMock()
            tab.update_data(player_data)

            self.assertEqual(tab.live_data, player_data)

    def test_override_overlay_with_no_data(self):
        with patch('overlay.tab_override.settings') as mock_settings:
            mock_settings.team_colors = [(0, 0, 0, 0)]
            mock_settings.civ_stats_color = "#000000"
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12

            tab = OverrideTab(MagicMock())
            tab.changed_data = {}

            # Should not emit when changed_data is empty
            tab.data_override = MagicMock()
            tab.override_overlay()
            tab.data_override.emit.assert_not_called()

    def test_override_overlay_with_data(self):
        with patch('overlay.tab_override.settings') as mock_settings:
            mock_settings.team_colors = [(0, 0, 0, 0)]
            mock_settings.civ_stats_color = "#000000"
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12

            tab = OverrideTab(MagicMock())
            tab.changed_data = {'map': 'Test Map', 'players': []}

            tab.data_override = MagicMock()
            tab.override_overlay()
            tab.data_override.emit.assert_called_once_with(tab.changed_data)


if __name__ == '__main__':
    unittest.main()
