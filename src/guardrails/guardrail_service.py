import os
from pathlib import Path
from typing import Optional

from nemoguardrails import LLMRails, RailsConfig

# TODO: fix this import path to match where your Settings class
# actually lives, e.g.:
#   from src.config.settings import settings
from src.configure.settings import get_settings

# NeMo Guardrails reads API keys from os.environ directly (per the
# api_key_env_var: OPENROUTER_API_KEY line in config.yml). Your
# pydantic Settings object loads the key from .env into its own
# field, but does NOT mirror it into os.environ automatically — so
# we do that explicitly here, once, before RailsConfig is built.
settings = get_settings()
os.environ.setdefault("OPENROUTER_API_KEY", settings.openrouter_api_key)


class GuardrailService:
    """
    Wraps NeMo Guardrails' LLMRails. This is expensive to construct
    (loads + compiles all Colang flows), so it must be created ONCE
    and reused — never instantiate this per-request.
    """

    def __init__(self):
        config_path = Path(__file__).parent
        self.config = RailsConfig.from_path(str(config_path))
        self.rails = LLMRails(self.config)

    async def generate(
        self,
        user_message: str,
        history: Optional[list[dict]] = None,
    ) -> str:
        messages = (history or []) + [
            {"role": "user", "content": user_message}
        ]

        response = await self.rails.generate_async(messages=messages)

        content = response.get("content")
        if content is None:
            raise RuntimeError(
                f"Guardrails returned no content. Raw response: {response}"
            )
        return content


_guardrail_service: Optional[GuardrailService] = None


def get_guardrail_service() -> GuardrailService:
    global _guardrail_service
    if _guardrail_service is None:
        _guardrail_service = GuardrailService()
    return _guardrail_service