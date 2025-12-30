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

# Mock other external modules
sys.modules['requests'] = MagicMock()
sys.modules['appdirs'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock
sys.modules['keyboard'] = MagicMock()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.tab_random import RandomTab


class TestTabRandom(unittest.TestCase):

    def test_random_tab_init(self):
        tab = RandomTab(MagicMock())
        self.assertTrue(hasattr(tab, 'civ_label'))
        self.assertTrue(hasattr(tab, 'civ_image'))
        self.assertTrue(hasattr(tab, 'map_label'))

    @patch('overlay.tab_random.random.choice')
    def test_randomize_logic(self, mock_choice):
        tab = RandomTab(MagicMock())
        mock_choice.return_value = "English"

        # Check that the randomize methods exist
        self.assertTrue(callable(tab.randomize_civ))
        self.assertTrue(callable(tab.randomize_map))


if __name__ == '__main__':
    unittest.main()
