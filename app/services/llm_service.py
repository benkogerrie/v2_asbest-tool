import os, json, httpx, logging, asyncio
from pydantic import BaseModel, ValidationError
from app.schemas.ai_output import AIOutput

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "anthropic")
        self.model = os.getenv("AI_MODEL", "claude-3-5-sonnet")
        self.api_key = os.getenv("AI_API_KEY")
        self.timeout = int(os.getenv("AI_TIMEOUT", "60"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "4000"))

    async def call(self, system_prompt: str, user_prompt: str) -> AIOutput:
        if self.provider == "anthropic":
            return await self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == "openai":
            return await self._call_openai(system_prompt, user_prompt)
        else:
            raise RuntimeError(f"Unsupported provider {self.provider}")

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> AIOutput:
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": self.api_key, "content-type": "application/json"}
        body = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": self.max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            text = data["content"][0]["text"]
            return self._parse_json(text)

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> AIOutput:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self.max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return self._parse_json(text)

    def _parse_json(self, text: str) -> AIOutput:
        try:
            data = json.loads(text)
            return AIOutput(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error("AI output parse error: %s", e)
            raise
