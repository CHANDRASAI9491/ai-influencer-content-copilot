def test_security_multi_tenant_isolation(client):
    # 1. Register User A
    res_a = client.post("/api/auth/register", json={
        "email": "usera@test.com",
        "password": "Password123!",
        "display_name": "User A"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    res_b = client.post("/api/auth/register", json={
        "email": "userb@test.com",
        "password": "Password123!",
        "display_name": "User B"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A generates an idea and brief
    idea_res = client.post("/api/ideas/generate", headers=headers_a, json={
        "goal": "Educate",
        "available_time": "30 minutes"
    })
    idea_a_id = idea_res.json()[0]["id"]

    brief_res = client.post("/api/briefs/generate", headers=headers_a, json={
        "idea_id": idea_a_id
    })
    brief_a_id = brief_res.json()["id"]

    # 4. User B attempts to access User A's idea -> MUST 404 (isolation)
    b_idea_get = client.get(f"/api/ideas/{idea_a_id}", headers=headers_b)
    assert b_idea_get.status_code == 404

    # 5. User B attempts to edit User A's brief -> MUST 404 (isolation)
    b_brief_edit = client.put(f"/api/briefs/{brief_a_id}", headers=headers_b, json={
        "title": "Hacked Title"
    })
    assert b_brief_edit.status_code == 404

    # 6. Unauthenticated requests must return 401
    unauth_res = client.get(f"/api/briefs/{brief_a_id}")
    assert unauth_res.status_code == 401


def test_feedback_system(client):
    # Register user
    res = client.post("/api/auth/register", json={
        "email": "feedback_user@test.com",
        "password": "Password123!",
        "display_name": "Feedback User"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit feedback with reason
    fb_res = client.post("/api/feedback", headers=headers, json={
        "rating": "not_useful",
        "reason": "Too generic",
        "details": "Need more specific exercises for lower back."
    })
    assert fb_res.status_code == 201
    data = fb_res.json()
    assert data["rating"] == "not_useful"
    assert data["reason"] == "Too generic"

    # List feedback
    list_res = client.get("/api/feedback", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
