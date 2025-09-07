import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.prompt import Prompt, PromptOverride

class PromptService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_prompt(self, name: str, tenant_id: str | None = None) -> str:
        # 1) Base prompt
        res = await self.session.execute(
            select(Prompt).where(Prompt.name == name, Prompt.status == "active").order_by(Prompt.version.desc())
        )
        prompt = res.scalar_one_or_none()
        if not prompt:
            raise RuntimeError(f"No active prompt found for {name}")

        content = prompt.content

        # 2) Tenant override (if exists)
        if tenant_id:
            res_override = await self.session.execute(
                select(PromptOverride).where(
                    PromptOverride.prompt_id == prompt.id,
                    PromptOverride.scope == f"tenant:{tenant_id}",
                    PromptOverride.status == "active"
                )
            )
            override = res_override.scalar_one_or_none()
            if override:
                content = override.content_override

        return content

    def inject_placeholders(self, content: str, mapping: dict[str, str]) -> str:
        out = content
        for key, value in mapping.items():
            out = out.replace(f"{{{{{key}}}}}", value)
        return out
