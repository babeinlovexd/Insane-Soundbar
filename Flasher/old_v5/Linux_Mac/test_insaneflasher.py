import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mocking external dependencies before importing InsaneFlasher
class MockCTk:
    def __init__(self, *args, **kwargs):
        pass

mock_ctk = MagicMock()
mock_ctk.CTk = MockCTk
sys.modules['customtkinter'] = mock_ctk

mock_modules = [
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

# Now we can import the function to test
from InsaneFlasher import get_app_dir

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

    def test_check_for_updates_invisible_chars(self):
        from InsaneFlasher import InsaneFlasher

        # Since InsaneFlasher inherits from a mocked customtkinter.CTk, we can't easily instantiate it.
        # We can just extract the function and call it with a mocked 'self'
        app = MagicMock()
        app.fw_label = MagicMock()
        app.flash_btn = MagicMock()

        # Scenario: Online version has a null byte and 'v', local version has 'V' and newline
        app.online_version = "v5.5.6\x00"
        local_version = "V5.5.6\n"

        # Test the update check function
        InsaneFlasher.check_for_updates(app, local_version)

        # It should correctly strip both and recognize them as identical
        app.fw_label.configure.assert_called_with(text="✅ WROOM ist aktuell (Version 5.5.6)", text_color="#2ecc71")
        app.flash_btn.configure.assert_called_with(state="disabled", text="KEIN UPDATE NÖTIG", fg_color="#333333")

if __name__ == '__main__':
    unittest.main()
