import unittest
from unittest.mock import MagicMock, patch
import os
from core.api_client import AIClient
from core.screen_capture import capture_screen_as_base64
from core.audio import speak_text

class TestCoreLogic(unittest.TestCase):

    def test_screen_capture(self):
        # Since we are in a headless environment, ImageGrab might fail or return black/empty.
        # But we can check if the function runs without erroring out on import/call logic.
        # We will mock ImageGrab for the sake of the test running in CI/CD environments.
        with patch('core.screen_capture.ImageGrab.grab') as mock_grab:
            # Create a mock image object
            mock_image = MagicMock()
            mock_grab.return_value = mock_image

            # Mock the save method to write to the BytesIO buffer
            def side_effect(buffer, format):
                buffer.write(b'fakeimagebytes')
            mock_image.save.side_effect = side_effect

            result = capture_screen_as_base64()
            self.assertIsNotNone(result)
            self.assertTrue(len(result) > 0)

    def test_api_client_init(self):
        client = AIClient(api_key="test_key")
        self.assertEqual(client.model, "gpt-4o")
        self.assertEqual(client.conversation_history, [])

    @patch('core.api_client.openai.OpenAI')
    def test_api_client_send_query(self, mock_openai):
        client = AIClient(api_key="test_key")

        # Mock the API response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "This is a test response."
        client.client.chat.completions.create.return_value = mock_completion

        response = client.send_query(prompt="Test prompt", image_base64="fakebase64", include_history=True)

        self.assertEqual(response, "This is a test response.")
        # Check history update
        self.assertEqual(len(client.conversation_history), 2)
        self.assertEqual(client.conversation_history[0]['role'], "user")
        self.assertEqual(client.conversation_history[1]['content'], "This is a test response.")

    @patch('core.audio.pyttsx3.init')
    def test_audio_speak(self, mock_init):
        # Test that speak_text calls the engine methods
        # Note: speak_text runs in a thread, so we might need to wait or just verify the function logic manually.
        # However, for unit testing threaded code, it's often better to mock threading.Thread to run synchronously
        # or just trust the mock call logic.

        with patch('threading.Thread') as mock_thread:
            speak_text("Hello world")
            mock_thread.assert_called_once()

            # Start the thread
            args = mock_thread.call_args[1]
            target = args['target']

            # Mock engine
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine

            # Execute target function
            target()

            mock_engine.say.assert_called_with("Hello world")
            mock_engine.runAndWait.assert_called_once()

if __name__ == '__main__':
    unittest.main()
