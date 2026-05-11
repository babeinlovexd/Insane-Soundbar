import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mocking external dependencies before importing InsaneFlasher
mock_modules = [
    'customtkinter',
    'tkinter',
    'tkinter.messagebox',
    'requests',
    'PIL',
    'zeroconf',
    'esptool',
    'serial',
    'serial.urlhandler',
    'serial.urlhandler.protocol_socket'
]

for module in mock_modules:
    sys.modules[module] = MagicMock()

# Now we can import the functions to test
from InsaneFlasher import get_app_dir, get_config_path, get_firmware_path

class TestGetAppDir(unittest.TestCase):

    @patch('os.name', 'nt')
    @patch('os.getenv')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_get_app_dir_windows(self, mock_makedirs, mock_exists, mock_getenv):
        # Scenario 1: Windows environment ('nt') where APPDATA is set
        mock_getenv.return_value = 'C:\\Users\\Test\\AppData\\Roaming'
        mock_exists.return_value = False

        expected_dir = os.path.join('C:\\Users\\Test\\AppData\\Roaming', 'InsaneFlasher')
        result = get_app_dir()

        self.assertEqual(result, expected_dir)
        mock_makedirs.assert_called_once_with(expected_dir)

    @patch('os.name', 'posix')
    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_get_app_dir_posix(self, mock_makedirs, mock_exists, mock_expanduser):
        # Scenario 2: Non-Windows environment where os.path.expanduser('~') is used
        mock_expanduser.return_value = '/home/testuser'
        mock_exists.return_value = False

        expected_dir = os.path.join('/home/testuser', 'InsaneFlasher')
        result = get_app_dir()

        self.assertEqual(result, expected_dir)
        mock_makedirs.assert_called_once_with(expected_dir)

    @patch('os.name', 'posix')
    @patch('os.path.expanduser')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_get_app_dir_already_exists(self, mock_makedirs, mock_exists, mock_expanduser):
        # Scenario 3: Verify that os.makedirs is NOT called if the directory already exists
        mock_expanduser.return_value = '/home/testuser'
        mock_exists.return_value = True

        get_app_dir()

        mock_makedirs.assert_not_called()

class TestConfigPaths(unittest.TestCase):

    @patch('InsaneFlasher.get_app_dir')
    def test_get_config_path(self, mock_get_app_dir):
        mock_get_app_dir.return_value = '/fake/app/dir'
        expected = os.path.join('/fake/app/dir', 'iss_favorites.json')
        self.assertEqual(get_config_path(), expected)

    @patch('InsaneFlasher.get_app_dir')
    def test_get_firmware_path(self, mock_get_app_dir):
        mock_get_app_dir.return_value = '/fake/app/dir'
        expected = os.path.join('/fake/app/dir', 'latest_firmware.bin')
        self.assertEqual(get_firmware_path(), expected)

if __name__ == '__main__':
    unittest.main()
