import pytest
from fastapi.testclient import TestClient

@pytest.mark.anyio
async def test_prompt_crud_and_test_run(client: TestClient, auth_override, monkeypatch):
    # 1) Create Prompt (draft)
    response = client.post("/admin/prompts", json={
        "name": "analysis_v1",
        "role": "system",
        "content": "# v1\n{{CHECKLIST}}\n{{SEVERITY_WEIGHTS}}\n{{OUTPUT_SCHEMA}}",
        "version": 1,
        "status": "draft"
    })
    assert response.status_code == 200
    prompt = response.json()
    pid = prompt["id"]

    # 2) Activate
    response = client.post(f"/admin/prompts/{pid}/activate")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    # 3) List
    response = client.get("/admin/prompts")
    assert response.status_code == 200
    assert any(p["id"] == pid for p in response.json())

    # 4) Update content + version
    response = client.put(f"/admin/prompts/{pid}", json={"content": "# v2", "version": 2})
    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert response.json()["content"] == "# v2"

    # 5) Create Override (draft)
    response = client.post(f"/admin/prompts/{pid}/overrides", json={
        "scope": "tenant:alpha",
        "content_override": "# tenant alpha\n...",
        "status": "draft"
    })
    assert response.status_code == 200
    override = response.json()
    oid = override["id"]

    # 6) Activate override
    response = client.post(f"/admin/prompts/overrides/{oid}/activate")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    # 7) List overrides
    response = client.get(f"/admin/prompts/{pid}/overrides")
    assert response.status_code == 200
    assert any(o["id"] == oid for o in response.json())

    # 8) Mock LLMService.call
    from app.services.llm_service import LLMService
    from app.schemas.ai_output import AIOutput, AIFinding
    
    async def mock_call(system_prompt: str, user_prompt: str):
        return AIOutput(
            report_summary="Test samenvatting",
            score=88.0,
            findings=[
                AIFinding(
                    code="DOC.MISS_SCOPE",
                    title="Ontbrekende scope",
                    category="FORMAL",
                    severity="HIGH",
                    status="FAIL",
                    page=1,
                    evidence_snippet="Geen sectie 'scope van onderzoek' gevonden.",
                    suggested_fix="Voeg een sectie toe."
                )
            ]
        )
    
    monkeypatch.setattr(LLMService, "call", mock_call)

    # 9) Test-run
    response = client.post(f"/admin/prompts/{pid}/test-run", json={
        "sample_text": "Dit is een testdocument zonder scope sectie.",
        "checklist": "- scope van onderzoek",
        "provider": "anthropic",
        "model": "claude-3-5-sonnet"
    })
    assert response.status_code == 200
    data = response.json()
    assert "parsed" in data
    assert data["parsed"]["score"] == 88.0
    assert data["parsed"]["findings"][0]["code"] == "DOC.MISS_SCOPE"

    # 10) Archive & Delete
    response = client.post(f"/admin/prompts/{pid}/archive")
    assert response.status_code == 200
    response = client.delete(f"/admin/prompts/{pid}")
    assert response.status_code == 200
