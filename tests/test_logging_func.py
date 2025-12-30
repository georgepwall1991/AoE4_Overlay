import sys
import os
import unittest
import tempfile
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules['appdirs'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.logging_func import get_logger, catch_exceptions

class TestLoggingFunc(unittest.TestCase):

    def test_get_logger(self):
        logger = get_logger("test_logger")
        self.assertEqual(logger.name, "test_logger")
        self.assertTrue(len(logger.handlers) > 0)

    def test_catch_exceptions_decorator(self):
        mock_logger = MagicMock()
        
        @catch_exceptions(mock_logger)
        def failing_func():
            raise ValueError("test error")
            
        # Should not raise exception
        failing_func()
        
        # Should have logged the exception
        mock_logger.exception.assert_called()

if __name__ == '__main__':
    unittest.main()
