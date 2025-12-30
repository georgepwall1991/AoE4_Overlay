import sys
import os
import unittest
import tempfile
from unittest.mock import MagicMock, patch

# Clear any cached modules first (but not test modules)
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay' or mod_name.startswith('PyQt5'):
        del sys.modules[mod_name]

# Mock dependencies before everything
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

from overlay.overlay_widget import set_pixmap, PIXMAP_CACHE, PlayerWidget, AoEOverlay


class TestOverlayWidget(unittest.TestCase):

    def setUp(self):
        PIXMAP_CACHE.clear()

    @patch('overlay.overlay_widget.file_path')
    def test_set_pixmap_caching(self, mock_file_path):
        from PyQt5.QtGui import QPixmap
        mock_widget = MagicMock()
        mock_widget.width.return_value = 100
        mock_widget.height.return_value = 100

        mock_file_path.return_value = "/fake/path/english.webp"

        # First call - should load and cache
        set_pixmap("english", mock_widget)
        self.assertEqual(len(PIXMAP_CACHE), 1)
        self.assertIn("english", PIXMAP_CACHE)

        # Second call - should use cache (widget.setPixmap called with cached value)
        set_pixmap("english", mock_widget)
        self.assertEqual(len(PIXMAP_CACHE), 1)  # Still only 1 item in cache

    def test_player_widget_update(self):
        mock_layout = MagicMock()
        with patch('overlay.overlay_widget.settings') as mock_settings:
            mock_settings.civ_stats_color = "#000000"
            mock_settings.team_colors = [(0, 0, 0, 0)]

            pw = PlayerWidget(0, mock_layout)

            player_data = {
                'civ': 'English', 'name': 'TestPlayer', 'country': 'US', 'team': 1,
                'rating': '1200', 'rank': '#1', 'winrate': '50%', 'wins': 10, 'losses': '10',
                'civ_games': '5', 'civ_winrate': '60%', 'civ_win_length_median': '20:00'
            }

            with patch('overlay.overlay_widget.set_pixmap'), \
                 patch('overlay.overlay_widget.set_country_flag'):
                pw.update_player(player_data)

            # PlayerWidget.name is a MockQLabel with setText method
            self.assertEqual(pw.name._text, 'TestPlayer')

    def test_aoe_overlay_init(self):
        with patch('overlay.overlay_widget.settings') as mock_settings:
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12
            mock_settings.civ_stats_color = "#000000"
            mock_settings.open_overlay_on_new_game = True

            overlay = AoEOverlay()

            # Check that players list was initialized
            self.assertEqual(len(overlay.players), 8)
            self.assertTrue(overlay.hiding_civ_stats)

    def test_aoe_overlay_update(self):
        with patch('overlay.overlay_widget.settings') as mock_settings:
            mock_settings.overlay_geometry = None
            mock_settings.font_size = 12
            mock_settings.civ_stats_color = "#000000"
            mock_settings.open_overlay_on_new_game = True

            overlay = AoEOverlay()

            game_data = {
                'map': 'Arabia',
                'players': [{'civ': 'French', 'name': 'P1', 'country': 'US', 'team': 1,
                            'rating': '1200', 'rank': '#1', 'winrate': '50%',
                            'wins': 10, 'losses': '10', 'civ_games': '1',
                            'civ_winrate': '50%', 'civ_win_length_median': '15:00'}]
            }

            with patch('overlay.overlay_widget.set_pixmap'), \
                 patch('overlay.overlay_widget.set_country_flag'):
                overlay.update_data(game_data)

            # Map label should be updated
            self.assertEqual(overlay.map._text, 'Arabia')


if __name__ == '__main__':
    unittest.main()
