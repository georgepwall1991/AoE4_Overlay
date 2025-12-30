import sys
import os
import unittest
import json
import tempfile
from unittest.mock import MagicMock, patch

# Clear any cached overlay modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay':
        del sys.modules[mod_name]

# Mock PyQt5 and requests before importing overlay
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()
sys.modules['requests'] = MagicMock()

appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock

sys.modules['keyboard'] = MagicMock()

# Add src to path so we can import overlay
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the module - this will use our mocked requests
import overlay.helper_func as helper_func_module
from overlay.helper_func import zeroed, strtime, version_to_int, process_game, match_mode, version_check
from overlay.settings import settings

class TestHelperFunc(unittest.TestCase):

    def test_match_mode(self):
        # Test converting rating_type_id to leaderboard_id
        # QM_ids in aoe4_data.py are generally 1-4 mapped to something else? 
        # Logic: leaderboard_id = match['rating_type_id'] + 2
        # if convert_customs and not in QM_ids: leaderboard_id = 16 + num_slots/2
        
        # Case 1: Standard QM
        # Assuming QM_ids has 1, 2, 3, 4 etc. Let's assume rating_type_id 0 -> 2.
        # We need to know what QM_ids are.
        # Let's mock a case where it falls through to custom logic if not in QM_ids.
        
        match_data = {'rating_type_id': 100, 'num_slots': 2}
        # 100 + 2 = 102. If 102 not in QM_ids.
        # Then 16 + 2/2 = 17.
        self.assertEqual(match_mode(match_data, convert_customs=True), 17)

    def test_version_check_new_version(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({'version': '2.0.0', 'link': 'http://download'})
        helper_func_module.requests.get.return_value = mock_response

        link = version_check("1.0.0")
        self.assertEqual(link, 'http://download')

    def test_version_check_no_update(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({'version': '1.0.0', 'link': 'http://download'})
        helper_func_module.requests.get.return_value = mock_response

        link = version_check("1.0.0")
        self.assertEqual(link, "")

    def test_zeroed(self):
        self.assertEqual(zeroed(None), 0)
        self.assertEqual(zeroed(10), 10)
        self.assertEqual(zeroed(0), 0)

    def test_strtime(self):
        # 3661 seconds = 1 hour, 1 minute, 1 second
        self.assertEqual(strtime(3661, show_seconds=True), "1 hours 1 minutes 1 seconds")
        self.assertEqual(strtime(3600), "1 hours")
        self.assertEqual(strtime(60), "1 minutes")
        self.assertEqual(strtime(30), "0 minutes") # Default behavior for small deltas

    def test_version_to_int(self):
        self.assertEqual(version_to_int("1.0.0"), 1000000)
        self.assertEqual(version_to_int("1.4.8"), 1004008)
        self.assertTrue(version_to_int("1.5.0") > version_to_int("1.4.9"))

    def test_process_game_basic(self):
        # Mock settings
        settings.profile_id = 12345
        
        # Sample game data from API structure
        game_data = {
            'map': 'Dry Arabia',
            'leaderboard_id': 17,
            'started_at': '2023-01-01T00:00:00.000Z',
            'server': 'ukwest',
            'game_id': 999,
            'kind': 'rm_1v1',
            'teams': [
                [ # Team 0
                    {
                        'profile_id': 12345,
                        'name': 'Hero',
                        'civilization': 'english',
                        'country': 'gb',
                        'modes': {
                            'rm_1v1': {
                                'rating': 1200,
                                'rank': 100,
                                'wins_count': 10,
                                'losses_count': 5,
                                'win_rate': 66.6,
                                'civilizations': []
                            }
                        }
                    }
                ],
                [ # Team 1
                    {
                        'profile_id': 67890,
                        'name': 'Villain',
                        'civilization': 'french',
                        'country': 'fr',
                        'modes': {
                            'rm_1v1': {
                                'rating': 1100,
                                'rank': 200,
                                'wins_count': 8,
                                'losses_count': 8,
                                'win_rate': 50.0,
                                'civilizations': []
                            }
                        }
                    }
                ]
            ]
        }

        result = process_game(game_data)
        
        self.assertEqual(result['map'], 'Dry Arabia')
        self.assertEqual(len(result['players']), 2)
        
        # Check main player is sorted first (index 0)
        self.assertEqual(result['players'][0]['name'], 'Hero')
        self.assertEqual(result['players'][0]['civ'], 'English')
        self.assertEqual(result['players'][0]['team'], 1) # 0-indexed team + 1
        
        # Check opponent
        self.assertEqual(result['players'][1]['name'], 'Villain')
        self.assertEqual(result['players'][1]['team'], 2)

    def test_version_to_int_invalid_format(self):
        """Test version_to_int with non-numeric parts raises ValueError"""
        with self.assertRaises(ValueError):
            version_to_int("1.2.a")

    def test_version_to_int_empty_string(self):
        """Test version_to_int with empty string raises ValueError"""
        with self.assertRaises(ValueError):
            version_to_int("")

    def test_strtime_negative_value(self):
        """Test strtime with negative seconds"""
        # Negative values produce unusual output, should handle gracefully
        # With negative values, divmod behavior is interesting
        # -60 divmod 3600 = (-1, 3540) so it goes weird
        # Just verify it doesn't crash
        result = strtime(-60)
        self.assertIsInstance(result, str)

    def test_strtime_zero_seconds(self):
        """Test strtime with zero returns '0 minutes' or '0 seconds'"""
        self.assertEqual(strtime(0), "0 minutes")
        # With show_seconds=True, only shows "0 seconds" (no redundant "0 minutes")
        self.assertEqual(strtime(0, show_seconds=True), "0 seconds")

    def test_strtime_large_value(self):
        """Test strtime with large value (years)"""
        # 2 years in seconds = 2 * 31557600 = 63115200
        result = strtime(63115200)
        self.assertIn("2 years", result)

    def test_process_game_null_player_name(self):
        """Test process_game handles null player name"""
        settings.profile_id = 12345
        game_data = {
            'map': 'Test Map',
            'leaderboard_id': 17,
            'started_at': '2023-01-01T00:00:00.000Z',
            'server': 'test',
            'game_id': 1,
            'kind': 'rm_1v1',
            'teams': [[{
                'profile_id': 12345,
                'name': None,  # Null name
                'civilization': 'english',
                'country': 'gb',
                'modes': {}
            }]]
        }
        result = process_game(game_data)
        self.assertEqual(result['players'][0]['name'], '?')

    def test_process_game_missing_modes(self):
        """Test process_game handles player with missing modes"""
        settings.profile_id = 12345
        game_data = {
            'map': 'Test Map',
            'leaderboard_id': 17,
            'started_at': '2023-01-01T00:00:00.000Z',
            'server': 'test',
            'game_id': 1,
            'kind': 'rm_1v1',
            'teams': [[{
                'profile_id': 12345,
                'name': 'TestPlayer',
                'civilization': 'english',
                'country': 'gb',
                'modes': {}  # Empty modes
            }]]
        }
        result = process_game(game_data)
        # Should use defaults
        self.assertEqual(result['players'][0]['rating'], '0')
        self.assertEqual(result['players'][0]['wins'], '0')
        self.assertEqual(result['players'][0]['losses'], '0')


if __name__ == '__main__':
    unittest.main()
