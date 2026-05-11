import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestProxyFlasher(unittest.TestCase):

    def setUp(self):
        # We need to mock 'requests' and 'zeroconf' because they might not be installed
        # and they are imported at the top level of proxy_flasher_cli
        self.modules_patcher = patch.dict('sys.modules', {
            'requests': MagicMock(),
            'requests.exceptions': MagicMock(),
            'zeroconf': MagicMock()
        })
        self.modules_patcher.start()

        # Now we can import the function to test
        import proxy_flasher_cli
        self.proxy_flasher_cli = proxy_flasher_cli

    def tearDown(self):
        self.modules_patcher.stop()

    def test_setup_s3_proxy_wroom_success(self):
        with patch('proxy_flasher_cli.requests.post') as mock_post, \
             patch('proxy_flasher_cli.time.sleep') as mock_sleep:

            # Setup mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Call the function
            self.proxy_flasher_cli.setup_s3_proxy("192.168.1.100", "wroom")

            # Assertions
            expected_url = "http://192.168.1.100/button/wroom_flash_mode/press"
            mock_post.assert_called_once_with(expected_url, timeout=5)
            mock_response.raise_for_status.assert_called_once()
            mock_sleep.assert_called_once_with(2)

    def test_setup_s3_proxy_rp2354_success(self):
        with patch('proxy_flasher_cli.requests.post') as mock_post, \
             patch('proxy_flasher_cli.time.sleep') as mock_sleep:

            # Setup mock response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Call the function
            self.proxy_flasher_cli.setup_s3_proxy("192.168.1.100", "rp2354")

            # Assertions
            expected_url = "http://192.168.1.100/button/rp2354_flash_mode/press"
            mock_post.assert_called_once_with(expected_url, timeout=5)
            mock_response.raise_for_status.assert_called_once()
            mock_sleep.assert_called_once_with(2)

    def test_setup_s3_proxy_request_exception(self):
        with patch('proxy_flasher_cli.requests.post') as mock_post, \
             patch('proxy_flasher_cli.sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:

            # Setup mock to raise an exception
            mock_post.side_effect = Exception("Connection error")

            # Call the function
            self.proxy_flasher_cli.setup_s3_proxy("192.168.1.100", "wroom")

            # Assertions
            mock_exit.assert_called_once_with(1)
            mock_print.assert_any_call("Failed to communicate with S3 proxy API: Connection error")

    def test_setup_s3_proxy_http_error(self):
        with patch('proxy_flasher_cli.requests.post') as mock_post, \
             patch('proxy_flasher_cli.sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:

            # Setup mock response that raises HTTPError
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_post.return_value = mock_response

            # Call the function
            self.proxy_flasher_cli.setup_s3_proxy("192.168.1.100", "wroom")

            # Assertions
            mock_exit.assert_called_once_with(1)
            mock_print.assert_any_call("Failed to communicate with S3 proxy API: 404 Not Found")

if __name__ == '__main__':
    unittest.main()
