import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Clear any cached modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay' or mod_name.startswith('PyQt5'):
        del sys.modules[mod_name]

# Mock dependencies
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mock_pyqt import setup_pyqt_mocks
setup_pyqt_mocks()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from overlay.custom_widgets import VerticalLabel, CustomKeySequenceEdit


class TestCustomWidgets(unittest.TestCase):

    def test_vertical_label_init(self):
        color = MagicMock()
        label = VerticalLabel("Test", color)
        # VerticalLabel uses self.textlabel for the text, not self.text
        self.assertEqual(label.textlabel, "Test")
        self.assertEqual(label.color, color)

    def test_custom_key_sequence_edit_convert(self):
        # Test the static method directly - it's a pure function
        conv = CustomKeySequenceEdit.convert_hotkey
        # Test basic replacements
        self.assertEqual(conv("Num+A"), "A")  # Num+ is removed
        self.assertEqual(conv("scrolllock"), "scroll lock")
        self.assertEqual(conv("ScrollLock"), "scroll lock")
        # Test passthrough
        self.assertEqual(conv("Ctrl+A"), "Ctrl+A")
        self.assertEqual(conv("Shift+B"), "Shift+B")


if __name__ == '__main__':
    unittest.main()
