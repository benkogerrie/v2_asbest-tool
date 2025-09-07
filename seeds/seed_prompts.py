import asyncio
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.prompt import Prompt

# Pad naar de prompt file
PROMPT_FILE = Path(__file__).parent / "analysis_v1.md"

async def seed_prompts():
    async for session in get_db():
        # Check of analysis_v1 al bestaat
        res = await session.execute(
            select(Prompt).where(Prompt.name == "analysis_v1", Prompt.status == "active")
        )
        existing = res.scalar_one_or_none()

        if existing:
            print("✅ Prompt 'analysis_v1' bestaat al, skipping.")
            return

        content = PROMPT_FILE.read_text(encoding="utf-8")

        prompt = Prompt(
            id=uuid.uuid4(),
            name="analysis_v1",
            role="system",
            content=content,
            version=1,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(prompt)
        await session.commit()
        print("🎉 Prompt 'analysis_v1' seeded.")

if __name__ == "__main__":
    asyncio.run(seed_prompts())
