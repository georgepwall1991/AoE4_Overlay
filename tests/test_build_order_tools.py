import sys
import os
import unittest
import tempfile
import json
from unittest.mock import MagicMock, patch

# Clear any cached overlay modules first
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('overlay.') or mod_name == 'overlay' or mod_name.startswith('PyQt5'):
        del sys.modules[mod_name]

# Mock PyQt5
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from mock_pyqt import setup_pyqt_mocks
setup_pyqt_mocks()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock other dependencies
sys.modules['keyboard'] = MagicMock()
appdirs_mock = MagicMock()
appdirs_mock.user_data_dir.return_value = tempfile.gettempdir()
sys.modules['appdirs'] = appdirs_mock
sys.modules['requests'] = MagicMock()

from overlay.build_order_tools import (
    list_directory_files,
    check_valid_aoe4_build_order,
    check_valid_aoe4_build_order_from_string,
    split_multi_label_line,
    QLabelSettings,
    search_image_extension,
    civilization_flags,
    get_build_orders,
)


class TestBuildOrderTools(unittest.TestCase):

    def test_civilization_flags_data(self):
        """Test that civilization flags dictionary has expected entries"""
        self.assertIn('English', civilization_flags)
        self.assertIn('French', civilization_flags)
        self.assertIn('Chinese', civilization_flags)
        self.assertIn('Mongols', civilization_flags)
        self.assertIn('Holy Roman Empire', civilization_flags)
        self.assertTrue(len(civilization_flags) > 10)

    def test_split_multi_label_line_basic(self):
        """Test basic line splitting"""
        result = split_multi_label_line("@one@two@three@")
        self.assertEqual(result, ['one', 'two', 'three'])

    def test_split_multi_label_line_no_markers(self):
        """Test line without @ markers"""
        result = split_multi_label_line("no markers here")
        self.assertEqual(result, ['no markers here'])

    def test_split_multi_label_line_single_item(self):
        """Test single item between markers"""
        result = split_multi_label_line("@single@")
        self.assertEqual(result, ['single'])

    def test_split_multi_label_line_empty(self):
        """Test empty string"""
        result = split_multi_label_line("")
        self.assertEqual(result, [])

    def test_split_multi_label_line_leading_trailing_markers(self):
        """Test that leading/trailing empty parts are removed"""
        result = split_multi_label_line("@foo@bar@")
        self.assertEqual(result, ['foo', 'bar'])

        result = split_multi_label_line("foo@bar")
        self.assertEqual(result, ['foo', 'bar'])

    def test_qlabel_settings_defaults(self):
        """Test QLabelSettings with default values"""
        settings = QLabelSettings()
        self.assertIsNone(settings.text_color)
        self.assertFalse(settings.text_bold)
        self.assertIsNone(settings.text_alignment)
        self.assertIsNone(settings.background_color)
        self.assertIsNone(settings.image_width)
        self.assertIsNone(settings.image_height)

    def test_qlabel_settings_custom(self):
        """Test QLabelSettings with custom values"""
        settings = QLabelSettings(
            text_color=[255, 0, 0],
            text_bold=True,
            text_alignment='center',
            background_color=[0, 0, 255],
            image_width=100,
            image_height=50
        )
        self.assertEqual(settings.text_color, [255, 0, 0])
        self.assertTrue(settings.text_bold)
        self.assertEqual(settings.text_alignment, 'center')
        self.assertEqual(settings.background_color, [0, 0, 255])
        self.assertEqual(settings.image_width, 100)
        self.assertEqual(settings.image_height, 50)

    def test_qlabel_settings_invalid_alignment(self):
        """Test that invalid alignment is set to None"""
        settings = QLabelSettings(text_alignment='invalid')
        self.assertIsNone(settings.text_alignment)

    def test_qlabel_settings_valid_alignments(self):
        """Test valid alignment values"""
        for alignment in ['left', 'center', 'right']:
            settings = QLabelSettings(text_alignment=alignment)
            self.assertEqual(settings.text_alignment, alignment)

    def test_check_valid_aoe4_build_order_valid(self):
        """Test validation with a valid build order"""
        valid_bo = {
            'name': 'Test Build Order',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': ['Build houses', 'Send villagers to food']
                }
            ]
        }
        self.assertTrue(check_valid_aoe4_build_order(valid_bo))

    def test_check_valid_aoe4_build_order_list_civilizations(self):
        """Test validation with multiple civilizations"""
        valid_bo = {
            'name': 'Multi-civ Build Order',
            'civilization': ['English', 'French'],
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        self.assertTrue(check_valid_aoe4_build_order(valid_bo))

    def test_check_valid_aoe4_build_order_invalid_civilization(self):
        """Test validation with invalid civilization"""
        invalid_bo = {
            'name': 'Bad Civ',
            'civilization': 'InvalidCiv',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_empty_civ_list(self):
        """Test validation with empty civilization list"""
        invalid_bo = {
            'name': 'Empty Civ List',
            'civilization': [],
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_empty_build_order(self):
        """Test validation with empty build order list"""
        invalid_bo = {
            'name': 'Empty BO',
            'civilization': 'English',
            'build_order': []
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_missing_fields(self):
        """Test validation with missing required fields in step"""
        invalid_bo = {
            'name': 'Missing Fields',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    # Missing villager_count, age, resources, notes
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_invalid_population(self):
        """Test validation with non-integer population count"""
        invalid_bo = {
            'name': 'Invalid Pop',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 'six',  # Should be int
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_invalid_age(self):
        """Test validation with age > 4"""
        invalid_bo = {
            'name': 'Invalid Age',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 5,  # Max is 4
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_missing_resource(self):
        """Test validation with missing resource field"""
        invalid_bo = {
            'name': 'Missing Resource',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0},  # Missing stone
                    'notes': []
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_invalid_note_type(self):
        """Test validation with non-string note"""
        invalid_bo = {
            'name': 'Invalid Note',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': [123]  # Should be string
                }
            ]
        }
        self.assertFalse(check_valid_aoe4_build_order(invalid_bo))

    def test_check_valid_aoe4_build_order_from_string_valid(self):
        """Test validation from valid JSON string"""
        valid_str = json.dumps({
            'name': 'String Test',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        })
        self.assertTrue(check_valid_aoe4_build_order_from_string(valid_str))

    def test_check_valid_aoe4_build_order_from_string_invalid_json(self):
        """Test validation with invalid JSON"""
        self.assertFalse(check_valid_aoe4_build_order_from_string("not valid json"))

    def test_check_valid_aoe4_build_order_from_string_empty(self):
        """Test validation with empty string"""
        self.assertFalse(check_valid_aoe4_build_order_from_string(""))


class TestListDirectoryFiles(unittest.TestCase):

    def setUp(self):
        """Create temp directory with test files"""
        self.temp_dir = tempfile.mkdtemp()
        # Create test files
        with open(os.path.join(self.temp_dir, 'file1.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(self.temp_dir, 'file2.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(self.temp_dir, 'file3.txt'), 'w') as f:
            f.write('test')
        # Create subdirectory
        sub_dir = os.path.join(self.temp_dir, 'subdir')
        os.makedirs(sub_dir)
        with open(os.path.join(sub_dir, 'file4.json'), 'w') as f:
            f.write('{}')

    def tearDown(self):
        """Clean up temp directory"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_list_directory_files_all(self):
        """Test listing all files recursively"""
        files = list_directory_files(self.temp_dir)
        self.assertEqual(len(files), 4)

    def test_list_directory_files_json_only(self):
        """Test listing only JSON files"""
        files = list_directory_files(self.temp_dir, extension='.json')
        self.assertEqual(len(files), 3)
        for f in files:
            self.assertTrue(f.endswith('.json'))

    def test_list_directory_files_non_recursive(self):
        """Test listing files without recursion"""
        files = list_directory_files(self.temp_dir, recursive=False)
        self.assertEqual(len(files), 3)

    def test_list_directory_files_txt_only(self):
        """Test listing only TXT files"""
        files = list_directory_files(self.temp_dir, extension='.txt')
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.txt'))


class TestSearchImageExtension(unittest.TestCase):

    def setUp(self):
        """Create temp directory with test image files"""
        self.temp_dir = tempfile.mkdtemp()
        # Create test files with different extensions
        self.png_file = os.path.join(self.temp_dir, 'image.png')
        with open(self.png_file, 'w') as f:
            f.write('png data')
        self.jpg_file = os.path.join(self.temp_dir, 'photo.jpg')
        with open(self.jpg_file, 'w') as f:
            f.write('jpg data')

    def tearDown(self):
        """Clean up temp directory"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_search_image_extension_exact_match(self):
        """Test finding file with exact extension"""
        result = search_image_extension(self.png_file)
        self.assertEqual(result, self.png_file)

    def test_search_image_extension_find_png(self):
        """Test finding PNG when no extension provided"""
        base_path = os.path.join(self.temp_dir, 'image')
        result = search_image_extension(base_path)
        self.assertEqual(result, self.png_file)

    def test_search_image_extension_find_jpg(self):
        """Test finding JPG when no extension provided"""
        base_path = os.path.join(self.temp_dir, 'photo')
        result = search_image_extension(base_path)
        self.assertEqual(result, self.jpg_file)

    def test_search_image_extension_not_found(self):
        """Test returning None when file not found"""
        result = search_image_extension(os.path.join(self.temp_dir, 'nonexistent'))
        self.assertIsNone(result)


class TestGetBuildOrders(unittest.TestCase):

    def setUp(self):
        """Create temp directory with test build order files"""
        self.temp_dir = tempfile.mkdtemp()

        # Valid build order
        self.valid_bo = {
            'name': 'Valid BO',
            'civilization': 'English',
            'build_order': [
                {
                    'population_count': 6,
                    'villager_count': 5,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': ['Test']
                }
            ]
        }
        with open(os.path.join(self.temp_dir, 'valid.json'), 'w') as f:
            json.dump(self.valid_bo, f)

        # Another valid build order
        self.valid_bo2 = {
            'name': 'Another BO',
            'civilization': 'French',
            'build_order': [
                {
                    'population_count': 7,
                    'villager_count': 6,
                    'age': 1,
                    'resources': {'wood': 0, 'food': 50, 'gold': 0, 'stone': 0},
                    'notes': []
                }
            ]
        }
        with open(os.path.join(self.temp_dir, 'another.json'), 'w') as f:
            json.dump(self.valid_bo2, f)

        # Invalid JSON file
        with open(os.path.join(self.temp_dir, 'invalid.json'), 'w') as f:
            f.write('not valid json')

    def tearDown(self):
        """Clean up temp directory"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_build_orders_loads_valid(self):
        """Test that valid build orders are loaded"""
        orders = get_build_orders(self.temp_dir, check_valid_aoe4_build_order)
        self.assertEqual(len(orders), 2)

    def test_get_build_orders_filters_invalid(self):
        """Test that invalid build orders are filtered out"""
        # Validator that rejects everything
        def reject_all(data):
            return False

        orders = get_build_orders(self.temp_dir, reject_all)
        self.assertEqual(len(orders), 0)

    def test_get_build_orders_handles_invalid_json(self):
        """Test that invalid JSON files are handled gracefully"""
        # Should not raise, should just skip the invalid file
        orders = get_build_orders(self.temp_dir, check_valid_aoe4_build_order)
        # Should still load the 2 valid ones
        self.assertEqual(len(orders), 2)


if __name__ == '__main__':
    unittest.main()
