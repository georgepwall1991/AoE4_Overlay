import sys
import os
import unittest
import json
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# Mock dependencies
websockets_mock = MagicMock()
class ConnectionClosed(Exception): pass
class ConnectionClosedOK(ConnectionClosed): pass
class ConnectionClosedError(ConnectionClosed): pass

# Set them on the mock and in sys.modules
websockets_mock.exceptions.ConnectionClosed = ConnectionClosed
websockets_mock.exceptions.ConnectionClosedOK = ConnectionClosedOK
websockets_mock.exceptions.ConnectionClosedError = ConnectionClosedError
sys.modules['websockets'] = websockets_mock
sys.modules['websockets.exceptions'] = websockets_mock.exceptions
sys.modules['websockets.legacy.server'] = MagicMock()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.websocket import Websocket_manager

class TestWebsocket(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.wm = Websocket_manager(7307)

    def test_initialization(self):
        self.assertEqual(self.wm.port, 7307)
        self.assertEqual(len(self.wm.queues), 0)
        self.assertIsNone(self.wm.initial_message)

    @patch('asyncio.new_event_loop')
    @patch('threading.Thread')
    def test_run(self, mock_thread, mock_new_loop):
        self.wm.run()
        mock_thread.assert_called_once()
        self.assertTrue(mock_thread.call_args[1]['daemon'])

    @patch('asyncio.Queue')
    async def test_manager_connection(self, mock_queue_class):
        mock_ws = AsyncMock()
        mock_q = AsyncMock() # Don't spec a Mock
        mock_queue_class.return_value = mock_q
        
        # We need to run the manager coroutine
        # But it has a while True loop. We should mock the queue.get to raise an exception to exit.
        mock_q.get = AsyncMock(side_effect=[ "msg1", asyncio.CancelledError() ])
        
        with patch.object(self.wm, '_send_ws_message', new_callable=AsyncMock) as mock_send:
            try:
                await self.wm.manager(mock_ws, "/path")
            except asyncio.CancelledError:
                pass
        
        mock_send.assert_called()

    def test_send_updates_state(self):
        msg = {"type": "test"}
        self.wm.send(msg)
        self.assertEqual(self.wm.initial_message, msg)
        self.assertEqual(self.wm.last_message, msg)

    @patch('overlay.websocket.asyncio.create_task')
    def test_send_broadcasts_if_loop(self, mock_create_task):
        self.wm.loop = MagicMock()
        msg = {"type": "test"}
        self.wm.send(msg)
        self.wm.loop.call_soon_threadsafe.assert_called()

if __name__ == '__main__':
    unittest.main()
