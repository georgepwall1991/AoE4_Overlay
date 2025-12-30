import sys
import os
import unittest
import tempfile
import importlib
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
sys.modules['webbrowser'] = MagicMock()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Now import - these will use the mocks
from overlay.tab_games import MatchTableModel, MatchHistoryTab
from overlay.settings import settings


class TestMatchTableModel(unittest.TestCase):

    def setUp(self):
        settings.profile_id = 123
        self.model = MatchTableModel()

    def test_model_row_count_empty(self):
        self.assertEqual(self.model.rowCount(), 0)

    def test_model_row_count_with_matches(self):
        self.model._matches = [
            {'game_id': 1, 'teams': []},
            {'game_id': 2, 'teams': []}
        ]
        self.assertEqual(self.model.rowCount(), 2)

    def test_model_column_count(self):
        self.assertEqual(self.model.columnCount(), 8)

    def test_set_matches(self):
        matches = [{'game_id': 1, 'teams': []}]
        self.model.set_matches(matches)
        self.assertEqual(len(self.model._matches), 1)

    def test_add_matches_filters_duplicates(self):
        self.model._matches = [{'game_id': 1, 'teams': []}]
        self.model.add_matches([
            {'game_id': 1, 'teams': []},  # Duplicate
            {'game_id': 2, 'teams': []}   # New
        ])
        self.assertEqual(len(self.model._matches), 2)

    def test_get_match_at_valid(self):
        self.model._matches = [{'game_id': 1, 'teams': []}]
        match = self.model.get_match_at(0)
        self.assertEqual(match['game_id'], 1)

    def test_get_match_at_invalid(self):
        match = self.model.get_match_at(99)
        self.assertIsNone(match)


class TestMatchHistoryTab(unittest.TestCase):

    def setUp(self):
        settings.profile_id = 123

    def test_tab_init(self):
        tab = MatchHistoryTab(MagicMock())
        self.assertIsNotNone(tab.model)
        self.assertIsNotNone(tab.view)

    def test_clear_games(self):
        tab = MatchHistoryTab(MagicMock())
        tab.model._matches = [{'game_id': 1}]
        tab.clear_games()
        self.assertEqual(len(tab.model._matches), 0)

    def test_update_widgets_filters_ongoing(self):
        tab = MatchHistoryTab(MagicMock())
        # Mock the resize method
        tab.view.resizeRowsToContents = MagicMock()

        matches = [
            {'game_id': 1, 'ongoing': False, 'teams': []},
            {'game_id': 2, 'ongoing': True, 'teams': []},  # Should be filtered
            {'game_id': 3, 'ongoing': False, 'teams': []}
        ]
        tab.update_widgets(matches)

        # Only non-ongoing matches should be in the model
        self.assertEqual(len(tab.model._matches), 2)


if __name__ == '__main__':
    unittest.main()
