from types import SimpleNamespace
from unittest.mock import MagicMock

from app.ai.avatar_chain import AvatarChain


class DummyLLM:
    pass


def test_build_prompt_includes_product_and_params():
    chain = AvatarChain(llm=DummyLLM(), image_client=MagicMock())
    product = SimpleNamespace(name="Denim Jacket", category="Outerwear")
    preset_params = {"body_type": "athletic"}
    style_params = {"pose": "street"}

    prompt = chain.build_prompt(product, preset_params, style_params)

    assert "Denim Jacket" in prompt
    assert "athletic" in prompt
    assert "street" in prompt


def test_generate_avatar_images_calls_image_client_with_prompt_and_count():
    image_client = MagicMock()
    image_client.generate_images.return_value = ["img"]
    chain = AvatarChain(llm=DummyLLM(), image_client=image_client)

    urls = chain.generate_avatar_images(
        product=None,
        preset_params={"gender": "unisex"},
        style_params=None,
        image_count=2,
    )

    assert urls == ["img"]
    image_client.generate_images.assert_called_once()
    args, kwargs = image_client.generate_images.call_args
    assert kwargs["image_count"] == 2
