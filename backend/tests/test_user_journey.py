def test_complete_mvp_user_journey(client):
    """
    Test the complete MVP User Journey end-to-end:
    Landing Page / Register
          ↓
    Creator Onboarding / Profile Setup
          ↓
    Creator Dashboard
          ↓
    Generate Content Ideas (5 personalized ideas)
          ↓
    Select Idea
          ↓
    Generate Complete Content Brief
          ↓
    Edit Brief (Script & Shots)
          ↓
    Save to Workspace
          ↓
    Mark as Planned / Filmed / Published
          ↓
    Give Feedback
    """
    # 1. Sign up
    reg = client.post("/api/auth/register", json={
        "email": "fulljourney@creator.local",
        "password": "Secret123Password!",
        "display_name": "Journey Creator"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Complete Onboarding / Profile setup
    onboard = client.put("/api/profile", headers=headers, json={
        "creator_type": "Aspiring Influencer",
        "niches": ["Fitness"],
        "secondary_niches": ["Healthy Eating"],
        "languages": ["Telugu", "English"],
        "target_audience": "College students and beginners",
        "broad_location": "Hyderabad",
        "goals": ["Grow audience", "Educate"],
        "formats": ["Educational", "Tutorial"],
        "equipment": ["Smartphone"],
        "filming_time": "30 minutes",
        "environment": "Gym"
    })
    assert onboard.status_code == 200
    profile = onboard.json()
    assert profile["niches"] == ["Fitness"]

    # 3. Generate 5 Personalized Content Ideas
    ideas_res = client.post("/api/ideas/generate", headers=headers, json={
        "goal": "Grow audience",
        "available_time": "30 minutes",
        "equipment": ["Smartphone"],
        "environment": "Gym"
    })
    assert ideas_res.status_code == 200
    ideas = ideas_res.json()
    assert len(ideas) == 5
    for idea in ideas:
        assert idea["title"]
        assert idea["description"]
        assert idea["estimated_time"]
        assert idea["why_it_fits"]

    # 4. Select an idea
    chosen_idea = ideas[0]
    select_res = client.patch(f"/api/ideas/{chosen_idea['id']}/select", headers=headers)
    assert select_res.status_code == 200

    # 5. Generate Complete Content Brief
    brief_res = client.post("/api/briefs/generate", headers=headers, json={
        "idea_id": chosen_idea["id"],
        "creator_notes": "Emphasize beginner safety"
    })
    assert brief_res.status_code == 201
    brief = brief_res.json()
    assert brief["title"]
    assert len(brief["hooks"]) >= 2
    assert len(brief["script"]) >= 4
    assert len(brief["shots"]) >= 3
    assert brief["caption"]
    assert brief["cta"]

    # 6. Edit Brief (Script & Shots)
    new_script = brief["script"].copy()
    new_script[0]["content"] = "Custom opening hook for college students!"
    new_shots = brief["shots"].copy()
    new_shots[0]["description"] = "Close up on phone showing workout countdown"

    edit_res = client.put(f"/api/briefs/{brief['id']}", headers=headers, json={
        "title": brief["title"] + " (Edited)",
        "script": new_script,
        "shots": new_shots,
        "version": brief["version"]
    })
    assert edit_res.status_code == 200
    saved_brief = edit_res.json()
    assert "Custom opening hook" in saved_brief["script"][0]["content"]
    assert saved_brief["version"] == brief["version"] + 1

    # 7. Workflow progression: Planned -> Filmed -> Published
    film_res = client.patch(f"/api/briefs/{brief['id']}/status", headers=headers, json={
        "status": "filmed"
    })
    assert film_res.status_code == 200
    assert film_res.json()["status"] == "filmed"

    pub_res = client.patch(f"/api/briefs/{brief['id']}/status", headers=headers, json={
        "status": "published"
    })
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "published"

    # 8. Check Workspace summary
    summary_res = client.get("/api/workspace/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["published"] >= 1
    assert "self-reported" in summary["disclaimer"].lower()

    # 9. Give Feedback
    fb_res = client.post("/api/feedback", headers=headers, json={
        "idea_id": chosen_idea["id"],
        "brief_id": brief["id"],
        "rating": "useful",
        "details": "Great script breakdown, saved me at least an hour of planning!"
    })
    assert fb_res.status_code == 201
    assert fb_res.json()["rating"] == "useful"
