from typing import List


class ImageClient:
    def __init__(self, api_key: str, base_url: str, timeout: float = 10.0):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    def generate_images(self, prompt: str, image_count: int = 1) -> List[str]:
        """
        Integrates with external image generation API.
        In production, this would make HTTP calls. For now, returns stubbed URLs.
        """
        return [f"{self.base_url}/stubbed/{i}?prompt={hash(prompt)}" for i in range(image_count)]
