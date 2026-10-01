def test_ideas_and_briefs_lifecycle(client):
    # 1. Login demo
    res = client.post("/api/auth/demo")
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Generate 5 Ideas
    gen_res = client.post("/api/ideas/generate", headers=headers, json={
        "goal": "Grow audience",
        "available_time": "30 minutes",
        "equipment": ["Smartphone"],
        "environment": "Gym"
    })
    assert gen_res.status_code == 200
    ideas = gen_res.json()
    assert len(ideas) == 5
    for idea in ideas:
        assert idea["title"]
        assert idea["description"]
        assert idea["why_it_fits"]
        assert idea["status"] == "suggested"

    selected_idea = ideas[0]
    idea_id = selected_idea["id"]

    # 3. Select Idea
    sel_res = client.patch(f"/api/ideas/{idea_id}/select", headers=headers)
    assert sel_res.status_code == 200
    assert sel_res.json()["status"] == "selected"

    # 4. Generate Content Brief
    brief_res = client.post("/api/briefs/generate", headers=headers, json={
        "idea_id": idea_id,
        "creator_notes": "Keep tone energetic and friendly"
    })
    assert brief_res.status_code == 201
    brief = brief_res.json()
    assert brief["id"]
    assert brief["idea_id"] == idea_id
    assert len(brief["hooks"]) >= 2
    hook_types = [h["type"] for h in brief["hooks"]]
    assert "direct" in hook_types
    assert "curiosity" in hook_types
    assert len(brief["script"]) >= 4
    assert len(brief["shots"]) >= 3
    assert brief["caption"]
    assert brief["cta"]
    assert brief["status"] == "planned"
    assert brief["version"] >= 1

    brief_id = brief["id"]

    # 5. Edit Brief
    edit_res = client.put(f"/api/briefs/{brief_id}", headers=headers, json={
        "title": "Custom Edited Reel Title",
        "selected_hook_type": "curiosity",
        "cta": "Click the link in bio to download free gym plan!",
        "version": brief["version"]
    })
    assert edit_res.status_code == 200
    updated_brief = edit_res.json()
    assert updated_brief["title"] == "Custom Edited Reel Title"
    assert updated_brief["selected_hook_type"] == "curiosity"
    assert updated_brief["version"] == brief["version"] + 1

    # 6. Status transitions: planned -> filmed -> published
    status_res = client.patch(f"/api/briefs/{brief_id}/status", headers=headers, json={
        "status": "filmed"
    })
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "filmed"

    status_res2 = client.patch(f"/api/briefs/{brief_id}/status", headers=headers, json={
        "status": "published"
    })
    assert status_res2.status_code == 200
    assert status_res2.json()["status"] == "published"
