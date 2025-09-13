import json, httpx, logging, asyncio
from pydantic import BaseModel, ValidationError
from app.schemas.ai_output import AIOutput
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.ai_provider
        self.model = settings.ai_model
        self.api_key = settings.ai_api_key
        self.timeout = settings.ai_timeout
        self.max_tokens = settings.ai_max_tokens

    async def call(self, system_prompt: str, user_prompt: str) -> AIOutput:
        if self.provider == "anthropic":
            return await self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == "openai":
            return await self._call_openai(system_prompt, user_prompt)
        else:
            raise RuntimeError(f"Unsupported provider {self.provider}")

    async def _call_anthropic(self, system_prompt: str, user_prompt: str) -> AIOutput:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        body = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": self.max_tokens,
        }
        
        logger.info(f"Calling Anthropic API with model: {self.model}")
        logger.info(f"System prompt length: {len(system_prompt)}")
        logger.info(f"User prompt length: {len(user_prompt)}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=body)
            
            logger.info(f"Anthropic API response status: {resp.status_code}")
            
            if resp.status_code != 200:
                logger.error(f"Anthropic API error: {resp.status_code} - {resp.text}")
                raise Exception(f"Anthropic API error: {resp.status_code}")
            
            data = resp.json()
            logger.info(f"Anthropic API response data keys: {list(data.keys())}")
            
            if "content" not in data or not data["content"]:
                logger.error(f"Anthropic API returned no content: {data}")
                raise Exception("Anthropic API returned no content")
            
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
            # Log the raw response for debugging
            logger.info(f"AI raw response: {text[:500]}...")
            
            if not text or not text.strip():
                logger.error("AI returned empty response")
                raise ValueError("AI returned empty response")
            
            # Clean up markdown formatting and extract JSON
            cleaned_text = text.strip()
            
            # Find JSON block - look for ```json or just {
            json_start = -1
            if "```json" in cleaned_text:
                json_start = cleaned_text.find("```json") + 7
            elif cleaned_text.startswith("```json"):
                json_start = 7
            elif "{" in cleaned_text:
                json_start = cleaned_text.find("{")
            
            if json_start >= 0:
                # Extract from JSON start to end
                json_text = cleaned_text[json_start:]
                # Find the end of JSON (last })
                json_end = json_text.rfind("}")
                if json_end >= 0:
                    cleaned_text = json_text[:json_end + 1]
                else:
                    cleaned_text = json_text
            else:
                # Fallback: try to find JSON object
                if "{" in cleaned_text and "}" in cleaned_text:
                    start = cleaned_text.find("{")
                    end = cleaned_text.rfind("}") + 1
                    cleaned_text = cleaned_text[start:end]
            
            cleaned_text = cleaned_text.strip()
            
            data = json.loads(cleaned_text)
            return AIOutput(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error("AI output parse error: %s", e)
            logger.error("Raw response was: %s", text)
            raise
