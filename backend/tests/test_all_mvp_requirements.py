import pytest
from app.config import settings

def test_auth_logout_endpoint(client):
    reg = client.post("/api/auth/register", json={
        "email": "logout_tester@test.local",
        "password": "Password123!",
        "display_name": "Logout Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify authenticated
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200

    # Logout
    logout_res = client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"


def test_section_5_onboarding_full_fields(client):
    reg = client.post("/api/auth/register", json={
        "email": "onboarding_tester@test.local",
        "password": "Password123!",
        "display_name": "Onboard Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "creator_type": "Aspiring Influencer",
        "niches": ["Sustainable Woodworking"],  # Custom niche
        "secondary_niches": ["DIY Home Decor"],
        "languages": ["English", "Spanish"],
        "target_audience": "Beginner woodworkers and hobbyists",
        "broad_location": "Austin, Texas",
        "goals": ["Educate", "Build personal brand"],
        "formats": ["Tutorial", "Talking head"],
        "equipment": ["Smartphone", "Tripod"],
        "filming_time": "1 hour",
        "environment": "Garage Workshop",
        "experience_level": "Beginner",
        "preferred_duration": "30-60 seconds",
        "tone": "Simple, practical, energetic",
        "topics_liked": ["Safety tips", "Budget hand tools"],
        "topics_avoided": ["Expensive CNC machines"],
        "platforms": ["Instagram Reels", "YouTube Shorts"],
        "posting_frequency": "3-4 times a week"
    }

    res = client.put("/api/profile", headers=headers, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["niches"] == ["Sustainable Woodworking"]
    assert data["experience_level"] == "Beginner"
    assert data["preferred_duration"] == "30-60 seconds"
    assert data["tone"] == "Simple, practical, energetic"
    assert "Safety tips" in data["topics_liked"]
    assert "Expensive CNC machines" in data["topics_avoided"]
    assert "Instagram Reels" in data["platforms"]
    assert data["posting_frequency"] == "3-4 times a week"


def test_ideas_selection_and_deletion(client):
    reg = client.post("/api/auth/register", json={
        "email": "ideas_mgmt@test.local",
        "password": "Password123!",
        "display_name": "Ideas Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate ideas
    gen_res = client.post("/api/ideas/generate", headers=headers, json={})
    assert gen_res.status_code == 200
    ideas = gen_res.json()
    assert len(ideas) >= 1
    target_idea = ideas[0]

    # POST select
    sel_res = client.post(f"/api/ideas/{target_idea['id']}/select", headers=headers)
    assert sel_res.status_code == 200
    assert sel_res.json()["status"] == "selected"

    # GET idea by ID
    get_res = client.get(f"/api/ideas/{target_idea['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == target_idea["id"]

    # DELETE idea
    del_res = client.delete(f"/api/ideas/{target_idea['id']}", headers=headers)
    assert del_res.status_code == 204

    # Verify not found after delete
    get_after = client.get(f"/api/ideas/{target_idea['id']}", headers=headers)
    assert get_after.status_code == 404


def test_brief_20_fields_lifecycle_and_deletion(client):
    reg = client.post("/api/auth/register", json={
        "email": "brief_mgmt@test.local",
        "password": "Password123!",
        "display_name": "Brief Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate ideas then brief
    ideas = client.post("/api/ideas/generate", headers=headers, json={}).json()
    idea = ideas[0]

    brief_res = client.post("/api/briefs/generate", headers=headers, json={"idea_id": idea["id"]})
    assert brief_res.status_code == 201
    brief = brief_res.json()

    # Verify all 20 brief fields are present
    assert "title" in brief
    assert "content_objective" in brief
    assert "selected_hook_type" in brief
    assert "recommended_hook" in brief
    assert "hooks" in brief and len(brief["hooks"]) >= 2
    assert "script" in brief and len(brief["script"]) >= 4
    assert "shots" in brief and len(brief["shots"]) >= 3
    assert "caption" in brief
    assert "cta" in brief
    assert "hashtags" in brief
    assert "on_screen_text" in brief
    assert "requirements" in brief
    assert "editing_notes" in brief
    assert "b_roll_requirements" in brief
    assert "audio_requirements" in brief
    assert "assumptions" in brief
    assert "originality_notes" in brief
    assert "platform_notes" in brief
    assert "status" in brief
    assert "version" in brief

    # PUT status update (Section 18 endpoint)
    status_put = client.put(f"/api/briefs/{brief['id']}/status", headers=headers, json={"status": "filmed"})
    assert status_put.status_code == 200
    assert status_put.json()["status"] == "filmed"

    # POST regenerate hooks
    regen = client.post(f"/api/briefs/{brief['id']}/regenerate-hooks", headers=headers)
    assert regen.status_code == 200
    assert len(regen.json()["hooks"]) >= 2

    # DELETE brief
    del_b = client.delete(f"/api/briefs/{brief['id']}", headers=headers)
    assert del_b.status_code == 204

    # Verify not found
    get_b = client.get(f"/api/briefs/{brief['id']}", headers=headers)
    assert get_b.status_code == 404


def test_workspace_kanban_and_summary(client):
    reg = client.post("/api/auth/register", json={
        "email": "kanban_tester@test.local",
        "password": "Password123!",
        "display_name": "Kanban Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate idea and brief
    ideas = client.post("/api/ideas/generate", headers=headers, json={}).json()
    client.post("/api/briefs/generate", headers=headers, json={"idea_id": ideas[0]["id"]})

    # GET /api/workspace
    ws_res = client.get("/api/workspace", headers=headers)
    assert ws_res.status_code == 200
    ws_data = ws_res.json()
    assert "planned" in ws_data
    assert "filmed" in ws_data
    assert "published" in ws_data
    assert "archived" in ws_data
    assert len(ws_data["planned"]) >= 1

    # GET /api/workspace/summary
    sum_res = client.get("/api/workspace/summary", headers=headers)
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert sum_data["planned"] >= 1
    assert "self-reported" in sum_data["disclaimer"].lower()


def test_health_and_ai_diagnostic_endpoints(client):
    # Health check
    h_res = client.get("/api/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "ok"

    # Diagnostic endpoint (Section 30)
    diag_res = client.get("/api/ai/diagnostic")
    assert diag_res.status_code == 200
    diag = diag_res.json()
    assert "provider" in diag
    assert "model" in diag
    assert "key_present" in diag
    assert isinstance(diag["key_present"], bool)
    assert "generation_success" in diag
    assert isinstance(diag["generation_success"], bool)
    assert "fallback_used" in diag
    assert isinstance(diag["fallback_used"], bool)
    
    # Crucial security check: NEVER print the API key
    content_str = diag_res.text
    if settings.GEMINI_API_KEY:
        assert settings.GEMINI_API_KEY not in content_str


def test_personalization_loop_with_feedback(client):
    reg = client.post("/api/auth/register", json={
        "email": "feedback_loop@test.local",
        "password": "Password123!",
        "display_name": "Feedback Loop Tester"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate initial ideas
    ideas = client.post("/api/ideas/generate", headers=headers, json={}).json()
    idea1 = ideas[0]

    # Submit negative feedback: "too generic"
    fb_res = client.post("/api/feedback", headers=headers, json={
        "idea_id": idea1["id"],
        "rating": "not_useful",
        "reason": "Too generic",
        "details": "Needs to be way more specific to technical students"
    })
    assert fb_res.status_code == 201

    # Generate next batch of ideas - AI service will query negative feedback and inject it
    next_ideas = client.post("/api/ideas/generate", headers=headers, json={}).json()
    assert len(next_ideas) >= 1
    for nid in next_ideas:
        assert nid["title"]
        assert nid["description"]
