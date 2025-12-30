import sys
import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Clear any cached overlay modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay':
        del sys.modules[mod_name]

# Mock PyQt5 before importing overlay
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['keyboard'] = MagicMock()

# Use temp directory for config
temp_dir = tempfile.mkdtemp()

# Mock appdirs to return temp directory
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = temp_dir
sys.modules['appdirs'] = appdirs_mock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import logging_func (uses mocked appdirs)
import overlay.logging_func as logging_func  # noqa: F401

# Define temp config file path
temp_config_file = os.path.join(temp_dir, "config.json")


class TestSettings(unittest.TestCase):

    def setUp(self):
        """Clean up config file before each test"""
        self.config_file = temp_config_file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def test_default_values(self):
        """Test that default values are set correctly"""
        from overlay.settings import _Settings
        s = _Settings()
        self.assertEqual(s.websocket_port, 7307)
        self.assertEqual(s.interval, 15)
        self.assertIsNone(s.profile_id)
        self.assertIsNone(s.player_name)

    def test_load_nonexistent_file(self):
        """Test load when config file doesn't exist"""
        from overlay.settings import _Settings
        s = _Settings()
        # Should not raise, just return
        s.load()
        # Defaults should still be set
        self.assertEqual(s.websocket_port, 7307)

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_load_empty_file(self):
        """Test load handles empty config file"""
        # Create empty file
        with open(self.config_file, 'w') as f:
            f.write('')

        from overlay.settings import _Settings
        s = _Settings()
        # Should not raise - may warn about parse error
        s.load()
        # Defaults should still be set
        self.assertEqual(s.websocket_port, 7307)

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_load_invalid_json(self):
        """Test load handles corrupted JSON file"""
        with open(self.config_file, 'w') as f:
            f.write('{"invalid json: missing close brace')

        from overlay.settings import _Settings
        s = _Settings()
        # Should not raise - just warn
        s.load()
        # Defaults should still be set
        self.assertEqual(s.websocket_port, 7307)

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_load_valid_config(self):
        """Test load with valid config"""
        config = {
            'websocket_port': 9999,
            'interval': 30,
            'player_name': 'TestPlayer'
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

        from overlay.settings import _Settings
        s = _Settings()
        s.load()
        self.assertEqual(s.websocket_port, 9999)
        self.assertEqual(s.interval, 30)
        self.assertEqual(s.player_name, 'TestPlayer')

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_load_unknown_fields_accepted(self):
        """Test load accepts unknown fields in JSON (current behavior)"""
        config = {
            'websocket_port': 7307,
            'unknown_field': 'some_value',
            'another_unknown': 123
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

        from overlay.settings import _Settings
        s = _Settings()
        s.load()
        # Unknown fields are currently set as attributes
        self.assertTrue(hasattr(s, 'unknown_field'))
        self.assertEqual(s.unknown_field, 'some_value')

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_save_creates_file(self):
        """Test save creates config file"""
        from overlay.settings import _Settings
        s = _Settings()
        s.player_name = 'SavedPlayer'
        s.save()

        self.assertTrue(os.path.exists(self.config_file))

        with open(self.config_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['player_name'], 'SavedPlayer')

    @patch('overlay.settings.CONFIG_FILE', temp_config_file)
    def test_save_and_load_roundtrip(self):
        """Test that save and load preserve all values"""
        from overlay.settings import _Settings
        s = _Settings()
        s.player_name = 'RoundtripPlayer'
        s.websocket_port = 8888
        s.interval = 60
        s.save()

        # Create new instance and load
        s2 = _Settings()
        s2.load()
        self.assertEqual(s2.player_name, 'RoundtripPlayer')
        self.assertEqual(s2.websocket_port, 8888)
        self.assertEqual(s2.interval, 60)


if __name__ == '__main__':
    unittest.main()
