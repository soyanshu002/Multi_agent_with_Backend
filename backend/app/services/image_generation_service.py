"""Image generation service using Pollinations authenticated image API."""
import base64
from urllib.parse import quote
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Image generation using Pollinations image API."""

    async def generate_image(
        self,
        prompt: str,
        model_key: str = "pollinations",
        height: int = 768,
        width: int = 768,
        seed: int = 42,
        **kwargs,
    ) -> dict:
        if not prompt or not prompt.strip():
            return {
                "success": False,
                "error": "Prompt cannot be empty",
                "image_urls": [],
            }

        api_key = settings.POLLINATIONS_API_KEY.strip()
        if not api_key:
            return {
                "success": False,
                "error": "POLLINATIONS_API_KEY is missing. Create a free publishable key at https://enter.pollinations.ai and add it to backend/.env.",
                "image_urls": [],
            }

        try:
            safe_prompt = quote(prompt.strip(), safe="")
            image_url = f"https://gen.pollinations.ai/image/{safe_prompt}"
            params = {
                "width": max(256, min(int(width), 1024)),
                "height": max(256, min(int(height), 1024)),
                "seed": int(seed),
                "model": "flux",
                "enhance": "true",
                "nologo": "true",
                "safe": "false",
                "nofeed": "false",
                "transparent": "false",
            }

            headers = {"Authorization": f"Bearer {api_key}"}

            async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                response = await client.get(image_url, params=params, headers=headers)

            content_type = response.headers.get("content-type", "")
            if response.status_code != 200:
                error_text = response.text[:200]
                logger.error("Pollinations API error %s: %s", response.status_code, error_text)
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {error_text}",
                    "image_urls": [],
                }

            if "image/" not in content_type.lower():
                error_text = response.text[:200]
                logger.error("Pollinations returned non-image response: %s", error_text)
                return {
                    "success": False,
                    "error": f"Unexpected response from image API: {error_text}",
                    "image_urls": [],
                }

            b64 = base64.b64encode(response.content).decode("utf-8")
            mime_type = "image/png" if "png" in content_type.lower() else "image/jpeg"
            data_url = f"data:{mime_type};base64,{b64}"

            logger.info("Generated Pollinations image for prompt: %s", prompt[:80])
            return {
                "success": True,
                "image_urls": [data_url],
                "error": None,
            }

        except Exception as e:
            logger.error("Image generation error: %s", str(e))
            return {
                "success": False,
                "error": f"Error: {str(e)[:100]}",
                "image_urls": [],
            }


AVAILABLE_MODELS = {
    "pollinations": {
        "name": "Pollinations AI",
        "description": "Free with publishable key from enter.pollinations.ai",
    },
}


async def get_available_models() -> dict:
    return AVAILABLE_MODELS


async def generate_image(prompt: str, model_key: str = "pollinations", **kwargs) -> dict:
    service = ImageGenerationService()
    return await service.generate_image(prompt, model_key=model_key, **kwargs)