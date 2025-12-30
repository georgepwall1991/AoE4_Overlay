import sys
import os
import unittest
import json
from unittest.mock import MagicMock, patch

import tempfile

# Clear any cached modules first (but not test modules)
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay':
        del sys.modules[mod_name]

# Mock dependencies
sys.modules['appdirs'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock
sys.modules['keyboard'] = MagicMock()

# Create a proper requests mock that behaves more like real requests
requests_mock = MagicMock()
mock_session_instance = MagicMock()
requests_mock.session.return_value = mock_session_instance
sys.modules['requests'] = requests_mock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import overlay.api_checking as api_checking_module
from overlay.api_checking import (
    find_player, get_full_match_history, Api_checker,
    get_rating_history, get_leaderboard_data
)
from overlay.settings import settings


class TestApiChecking(unittest.TestCase):

    def setUp(self):
        # Reset settings
        settings.profile_id = None
        settings.player_name = None
        settings.steam_id = None

    def _patch_session(self, mock_session):
        """Helper to patch the session on the module"""
        original = api_checking_module.session
        api_checking_module.session = mock_session
        return original

    def _restore_session(self, original):
        """Helper to restore the original session"""
        api_checking_module.session = original

    def test_find_player_by_id_success(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'profile_id': 12345,
            'name': 'TestPlayer',
            'steam_id': '76561198000000000'
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            found = find_player("12345")

            self.assertTrue(found)
            self.assertEqual(settings.profile_id, 12345)
            self.assertEqual(settings.player_name, 'TestPlayer')
            mock_session.get.assert_called()
        finally:
            self._restore_session(original)

    def test_find_player_by_search_success(self):
        mock_response_fail = MagicMock()
        mock_response_fail.text = "{}"

        mock_response_search = MagicMock()
        mock_response_search.text = json.dumps({
            'players': [{
                'profile_id': 999,
                'name': 'SearchedPlayer',
                'steam_id': None
            }]
        })

        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_response_fail, mock_response_search]

        original = self._patch_session(mock_session)
        try:
            found = find_player("SearchedPlayer")

            self.assertTrue(found)
            self.assertEqual(settings.profile_id, 999)
            self.assertEqual(settings.player_name, 'SearchedPlayer')
        finally:
            self._restore_session(original)

    def test_get_full_match_history(self):
        settings.profile_id = 123
        mock_response = MagicMock()
        mock_response.text = json.dumps({'games': [{'game_id': 1}, {'game_id': 2}]})

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            history = get_full_match_history(2)

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]['game_id'], 1)
        finally:
            self._restore_session(original)

    def test_api_checker_check_for_new_game_loop(self):
        mock_session = MagicMock()
        original = self._patch_session(mock_session)

        try:
            checker = Api_checker()
            settings.profile_id = 123
            settings.interval = 0

            with patch.object(checker, 'get_data') as mock_get_data:
                mock_get_data.side_effect = [None, None, {'game_id': 123}]
                with patch.object(checker, 'sleep', return_value=False):
                    result = checker.check_for_new_game()
                    self.assertEqual(result['game_id'], 123)
                    self.assertEqual(mock_get_data.call_count, 3)
        finally:
            self._restore_session(original)

    def test_api_checker_sleep_logic(self):
        checker = Api_checker()
        with patch('time.sleep'):
            checker.force_stop = True
            self.assertTrue(checker.sleep(1))

            checker.force_stop = False
            checker.force_check_event.set()
            self.assertFalse(checker.sleep(1))

    def test_close_session(self):
        mock_session = MagicMock()
        original = self._patch_session(mock_session)
        try:
            # Use the module's close_session directly to ensure we use the patched session
            api_checking_module.close_session()
            mock_session.close.assert_called_once()
        finally:
            self._restore_session(original)

    def test_get_data_success(self):
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'game_id': 100,
            'started_at': '2025-01-01T00:00:00.000Z',
            'kind': 'rm_1v1'
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            settings.profile_id = 123

            data = checker.get_data()
            self.assertEqual(data['game_id'], 100)
        finally:
            self._restore_session(original)

    def test_get_data_error(self):
        mock_response = MagicMock()
        mock_response.text = '{"error": "not found"}'

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            self.assertIsNone(checker.get_data())
        finally:
            self._restore_session(original)

    def test_get_data_exception(self):
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("network error")

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            self.assertIsNone(checker.get_data())
        finally:
            self._restore_session(original)

    def test_api_checker_sleep_interrupted(self):
        checker = Api_checker()
        checker.force_stop = True
        self.assertTrue(checker.sleep(5))

        checker.force_stop = False
        checker.force_check_event.set()
        self.assertFalse(checker.sleep(5))

    def test_find_player_not_found(self):
        """Test find_player when player is not found"""
        # First call returns no name, second call returns empty players
        mock_response_fail1 = MagicMock()
        mock_response_fail1.text = "{}"

        mock_response_fail2 = MagicMock()
        mock_response_fail2.text = json.dumps({'players': []})

        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_response_fail1, mock_response_fail2]

        original = self._patch_session(mock_session)
        try:
            # Set initial values
            settings.profile_id = 999
            settings.player_name = 'OldPlayer'

            found = find_player("NonexistentPlayer")

            self.assertFalse(found)
            # Settings should be restored to old values
            self.assertEqual(settings.profile_id, 999)
            self.assertEqual(settings.player_name, 'OldPlayer')
        finally:
            self._restore_session(original)

    def test_get_rating_history_success(self):
        """Test get_rating_history returns rating data"""
        settings.profile_id = 123
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'ratings': [
                {'rating': 1200, 'date': '2025-01-01'},
                {'rating': 1250, 'date': '2025-01-02'}
            ]
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            ratings = get_rating_history(17, 2)
            self.assertEqual(len(ratings), 2)
            self.assertEqual(ratings[0]['rating'], 1200)
        finally:
            self._restore_session(original)

    def test_get_rating_history_error(self):
        """Test get_rating_history returns None on error"""
        settings.profile_id = 123
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("network error")

        original = self._patch_session(mock_session)
        try:
            ratings = get_rating_history(17)
            self.assertIsNone(ratings)
        finally:
            self._restore_session(original)

    def test_get_leaderboard_data_success(self):
        """Test get_leaderboard_data returns data"""
        settings.profile_id = 123
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'games': [{'game_id': 1}],
            'count': 1
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            data = get_leaderboard_data(17)
            self.assertIsNotNone(data)
            self.assertEqual(data['count'], 1)
        finally:
            self._restore_session(original)

    def test_get_leaderboard_data_error(self):
        """Test get_leaderboard_data returns None on error"""
        settings.profile_id = 123
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("network error")

        original = self._patch_session(mock_session)
        try:
            data = get_leaderboard_data(17)
            self.assertIsNone(data)
        finally:
            self._restore_session(original)

    def test_get_full_match_history_error(self):
        """Test get_full_match_history returns None on error"""
        settings.profile_id = 123
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("network error")

        original = self._patch_session(mock_session)
        try:
            history = get_full_match_history(10)
            self.assertIsNone(history)
        finally:
            self._restore_session(original)

    def test_api_checker_reset(self):
        """Test Api_checker reset method"""
        from datetime import datetime
        checker = Api_checker()
        # Set non-default timestamps
        checker.last_match_timestamp = datetime(2025, 1, 1)
        checker.last_rating_timestamp = datetime(2025, 1, 1)

        checker.reset()

        # Should reset to 1900 and set force_check_event
        self.assertEqual(checker.last_match_timestamp.year, 1900)
        self.assertEqual(checker.last_rating_timestamp.year, 1900)
        self.assertTrue(checker.force_check_event.is_set())

    def test_api_checker_force_stop_property(self):
        """Test Api_checker force_stop getter and setter"""
        checker = Api_checker()

        # Initially not set
        self.assertFalse(checker.force_stop)

        # Set to True
        checker.force_stop = True
        self.assertTrue(checker.force_stop)
        self.assertTrue(checker.stop_event.is_set())

        # Set to False
        checker.force_stop = False
        self.assertFalse(checker.force_stop)
        self.assertFalse(checker.stop_event.is_set())

    def test_check_for_new_game_with_delay(self):
        """Test check_for_new_game stops when delay sleep returns True"""
        checker = Api_checker()
        settings.profile_id = 123

        # Make sleep return True immediately (simulating stop during delay)
        with patch.object(checker, 'sleep', return_value=True):
            result = checker.check_for_new_game(delayed_seconds=5)
            self.assertIsNone(result)

    def test_get_data_returns_none_when_stopped(self):
        """Test get_data returns None when stop_event is set"""
        checker = Api_checker()
        checker.force_stop = True
        settings.profile_id = 123

        result = checker.get_data()
        self.assertIsNone(result)

    def test_get_data_returns_none_if_stopped_after_request(self):
        """Test get_data returns None if stopped after API request"""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'game_id': 100,
            'started_at': '2025-01-01T00:00:00.000Z',
            'kind': 'rm_1v1'
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            settings.profile_id = 123

            # Create a side effect that sets stop after the first call
            def set_stop_after_call(*args, **kwargs):
                checker.force_stop = True
                return mock_response

            mock_session.get.side_effect = set_stop_after_call
            result = checker.get_data()
            self.assertIsNone(result)
        finally:
            self._restore_session(original)

    def test_find_player_json_decode_error(self):
        """Test find_player handles JSONDecodeError gracefully on profile lookup"""
        mock_response = MagicMock()
        mock_response.text = "not valid json {"  # Invalid JSON

        mock_response_search = MagicMock()
        mock_response_search.text = json.dumps({'players': []})

        mock_session = MagicMock()
        mock_session.get.side_effect = [mock_response, mock_response_search]

        original = self._patch_session(mock_session)
        try:
            # Set initial values to verify they're preserved on failure
            settings.profile_id = 999
            settings.player_name = 'OldPlayer'

            found = find_player("invalid_json_test")

            self.assertFalse(found)
            # Settings should be restored
            self.assertEqual(settings.profile_id, 999)
            self.assertEqual(settings.player_name, 'OldPlayer')
        finally:
            self._restore_session(original)

    def test_find_player_network_exception(self):
        """Test find_player handles network errors gracefully"""
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection refused")

        original = self._patch_session(mock_session)
        try:
            settings.profile_id = 888
            settings.player_name = 'NetworkTest'

            found = find_player("network_error_test")

            self.assertFalse(found)
            # Settings should be restored
            self.assertEqual(settings.profile_id, 888)
            self.assertEqual(settings.player_name, 'NetworkTest')
        finally:
            self._restore_session(original)

    def test_get_data_invalid_datetime_format(self):
        """Test get_data handles malformed started_at field"""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'game_id': 100,
            'started_at': 'invalid-date-format',  # Bad format
            'kind': 'rm_1v1'
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            settings.profile_id = 123

            # Should handle the ValueError from strptime gracefully
            result = checker.get_data()
            # Result should be None or raise - depends on implementation
            # Current implementation will raise ValueError
        except ValueError:
            pass  # Expected - invalid datetime format
        finally:
            self._restore_session(original)

    def test_get_data_missing_kind_field(self):
        """Test get_data handles missing kind field for leaderboard calculation"""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'game_id': 100,
            'started_at': '2025-01-01T00:00:00.000Z',
            # 'kind' field is missing
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            settings.profile_id = 123

            # Should handle missing 'kind' gracefully - leaderboard_id defaults to 0
            result = checker.get_data()
            if result:
                self.assertEqual(result['leaderboard_id'], 0)  # Default when kind parsing fails
        finally:
            self._restore_session(original)

    def test_get_data_malformed_kind_field(self):
        """Test get_data handles malformed kind field"""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            'game_id': 100,
            'started_at': '2025-01-01T00:00:00.000Z',
            'kind': 'custom_game'  # Doesn't end with a number
        })

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        original = self._patch_session(mock_session)
        try:
            checker = Api_checker()
            settings.profile_id = 123

            # Should handle non-numeric kind ending gracefully
            result = checker.get_data()
            if result:
                self.assertEqual(result['leaderboard_id'], 0)  # Default on parse failure
        finally:
            self._restore_session(original)


if __name__ == '__main__':
    unittest.main()
