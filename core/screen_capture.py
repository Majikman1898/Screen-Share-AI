import io
import base64
from PIL import ImageGrab

def capture_screen_as_base64():
    """Captures the current screen and returns it as a base64 encoded string."""
    try:
        screenshot = ImageGrab.grab()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return None

def capture_screen_to_file(filepath):
    """Captures the current screen and saves it to a file."""
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        return True
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return False
