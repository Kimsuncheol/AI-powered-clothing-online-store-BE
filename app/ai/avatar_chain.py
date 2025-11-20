from typing import Any, Dict, List, Optional

from app.core.image_client import ImageClient
from app.models.product import Product

AVATAR_SYSTEM_HINT = """
You generate detailed textual prompts for clothing try-on avatars.
You receive:
- product information (name, category, style, colors)
- avatar preset parameters (body type, gender, skin tone, style keywords)
- optional styleParams for pose, background, mood

Output a single, rich prompt string for an image generation model.
""".strip()


class AvatarChain:
    def __init__(self, llm: Any, image_client: ImageClient):
        self.llm = llm
        self.image_client = image_client

    def build_prompt(
        self,
        product: Optional[Product],
        preset_params: Dict[str, Any],
        style_params: Optional[Dict[str, Any]],
    ) -> str:
        base = f"Fashion avatar with preset {preset_params}"
        if product:
            base += f", wearing product '{product.name}' in category {product.category}"
        if style_params:
            base += f", with style settings {style_params}"
        return base

    def generate_avatar_images(
        self,
        *,
        product: Optional[Product],
        preset_params: Dict[str, Any],
        style_params: Optional[Dict[str, Any]],
        image_count: int,
    ) -> List[str]:
        prompt = self.build_prompt(product, preset_params, style_params)
        return self.image_client.generate_images(prompt=prompt, image_count=image_count)
