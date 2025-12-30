import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Clear any cached modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay' or mod_name.startswith('PyQt5'):
        del sys.modules[mod_name]

# Mock PyQt5
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mock_pyqt import setup_pyqt_mocks
setup_pyqt_mocks()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.worker import Worker, scheldule


class TestWorker(unittest.TestCase):

    def test_worker_run_success(self):
        def test_fn(x):
            return x * 2

        worker = Worker(test_fn, 10)
        # Mock signals with proper emit methods
        worker.signals = MagicMock()
        worker.signals.result = MagicMock()
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.result.emit.assert_called_with(20)
        worker.signals.finished.emit.assert_called_once()

    def test_worker_run_error(self):
        def test_fn():
            raise ValueError("fail")

        worker = Worker(test_fn)
        # Mock signals with proper emit methods
        worker.signals = MagicMock()
        worker.signals.result = MagicMock()
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        # Error should be emitted with tuple
        worker.signals.error.emit.assert_called()
        worker.signals.finished.emit.assert_called_once()
        # Result should not be emitted on error
        worker.signals.result.emit.assert_not_called()

    @patch('overlay.worker.THREADPOOL')
    def test_scheldule(self, mock_threadpool):
        callback = MagicMock()

        def test_fn():
            return 1

        scheldule(callback, test_fn)

        mock_threadpool.start.assert_called_once()

    def test_worker_init(self):
        def test_fn(x, y):
            return x + y

        worker = Worker(test_fn, 1, 2)

        self.assertEqual(worker.fn, test_fn)
        self.assertEqual(worker.args, (1, 2))


if __name__ == '__main__':
    unittest.main()
