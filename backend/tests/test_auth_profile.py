def test_register_and_profile_flow(client):
    # 1. Register new creator
    register_res = client.post("/api/auth/register", json={
        "email": "creator1@test.com",
        "password": "Password123!",
        "display_name": "Test Creator"
    })
    assert register_res.status_code == 201
    data = register_res.json()
    assert "access_token" in data
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile
    profile_res = client.get("/api/profile", headers=headers)
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile["creator_type"] == "Aspiring Influencer"

    # 3. Update Profile
    update_res = client.put("/api/profile", headers=headers, json={
        "creator_type": "Established Influencer",
        "niches": ["Tech", "AI Tools"],
        "languages": ["English", "Spanish"],
        "target_audience": "Junior developers",
        "equipment": ["Laptop", "Microphone"],
        "filming_time": "45 minutes",
        "environment": "Home Office"
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["creator_type"] == "Established Influencer"
    assert "AI Tools" in updated["niches"]
    assert updated["filming_time"] == "45 minutes"

def test_demo_login_and_reset(client):
    # 1. Instant demo login as Rahul
    demo_res = client.post("/api/auth/demo")
    assert demo_res.status_code == 200
    data = demo_res.json()
    assert data["user"]["display_name"] == "Rahul"
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check profile reflects Rahul's specs
    profile_res = client.get("/api/profile", headers=headers)
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert "Fitness" in profile["niches"]
    assert "Telugu" in profile["languages"]
    assert profile["environment"] == "Gym"
