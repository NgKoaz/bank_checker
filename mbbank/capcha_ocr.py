import io
from PIL import Image


class CaptchaProcessing:
    """
    Base class for capcha processing for self implemented
    Examples:
    ```py
    class MyCapchaProcessing(CapchaProcessing):
        def process_image(self, img: bytes) -> str:
            return "my_text"
    ```
    """

    def process_image(self, img: bytes) -> str:
        """
        Process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        raise NotImplementedError("process_image is not implemented")
    
