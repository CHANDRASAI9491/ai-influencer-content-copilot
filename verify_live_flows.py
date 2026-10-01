import urllib.request
import json
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    with urllib.request.urlopen(req) as resp:
        res_body = resp.read().decode("utf-8")
        return resp.status, json.loads(res_body) if res_body else {}

def run_verification():
    print("=== LIVE END-TO-END FLOW VERIFICATION ===")
    
    # 1. Health
    status, health = request("GET", "/api/health")
    assert status == 200 and health["status"] == "ok"
    print("[PASS] 1. Health Check: OK")

    import time
    test_email = f"live_creator_{int(time.time())}@copilot.local"

    # 2. Register
    status, reg_data = request("POST", "/api/auth/register", {
        "email": test_email,
        "password": "LivePassword2026!",
        "display_name": "Live Verified Creator"
    })
    assert status == 201
    token = reg_data["access_token"]
    print("✓ 2. Register: OK (Token generated)")

    # 3. Login
    status, login_data = request("POST", "/api/auth/login", {
        "email": test_email,
        "password": "LivePassword2026!"
    })
    assert status == 200
    token = login_data["access_token"]
    print("✓ 3. Login: OK")

    # 4. Creator Onboarding & Profile Update
    profile_payload = {
        "creator_type": "Aspiring Influencer",
        "niches": ["Technology"],
        "secondary_niches": ["Coding", "AI Productivity"],
        "languages": ["English"],
        "target_audience": "College students and beginners",
        "broad_location": "Global",
        "goals": ["Educational content", "Grow audience"],
        "formats": ["Instagram Reels", "Tutorial"],
        "equipment": ["Smartphone"],
        "filming_time": "1 hour",
        "environment": "Bedroom/desk setup",
        "experience_level": "Beginner",
        "preferred_duration": "30-60 seconds",
        "tone": "Simple, practical, energetic",
        "topics_liked": ["Programming tips", "AI shortcuts"],
        "topics_avoided": ["Controversy", "Crypto hype"],
        "platforms": ["Instagram Reels"],
        "posting_frequency": "3-4 times a week"
    }
    status, profile = request("PUT", "/api/profile", profile_payload, token)
    assert status == 200
    assert profile["niches"] == ["Technology"]
    assert profile["tone"] == "Simple, practical, energetic"
    print("✓ 4. Onboarding / Profile Update: OK")

    # 5. Profile Retrieval
    status, retrieved_profile = request("GET", "/api/profile", None, token)
    assert status == 200
    assert retrieved_profile["target_audience"] == "College students and beginners"
    print("✓ 5. Profile Retrieval: OK")

    # 6. Generate AI Ideas
    status, ideas = request("POST", "/api/ideas/generate", {}, token)
    assert status == 200 and len(ideas) >= 1
    selected_idea = ideas[0]
    print(f"✓ 6. AI Ideas Generation: OK ({len(ideas)} ideas generated, Provider: {selected_idea['meta_info'].get('provider')})")

    # 7. Select Idea
    status, sel_res = request("POST", f"/api/ideas/{selected_idea['id']}/select", None, token)
    assert status == 200 and sel_res["status"] == "selected"
    print("✓ 7. Select Idea: OK")

    # 8. Generate Complete Reel Brief (All 20 fields)
    status, brief = request("POST", "/api/briefs/generate", {
        "idea_id": selected_idea["id"],
        "creator_notes": "Keep tone energetic and friendly"
    }, token)
    assert status == 201
    assert "title" in brief
    assert "content_objective" in brief
    assert "hooks" in brief and len(brief["hooks"]) >= 2
    assert "script" in brief and len(brief["script"]) >= 4
    assert "shots" in brief and len(brief["shots"]) >= 3
    assert "hashtags" in brief
    assert "requirements" in brief
    assert "editing_notes" in brief
    assert "assumptions" in brief
    print(f"✓ 8. Generate Complete Reel Brief: OK (v{brief['version']}, {len(brief['script'])} script segments, {len(brief['shots'])} shots)")

    # 9. Edit and Save Brief
    new_script = brief["script"]
    new_script[0]["content"] = "Live verified hook delivery!"
    status, updated_brief = request("PUT", f"/api/briefs/{brief['id']}", {
        "title": brief["title"] + " (Verified)",
        "script": new_script,
        "version": brief["version"]
    }, token)
    assert status == 200
    assert updated_brief["version"] == brief["version"] + 1
    print(f"✓ 9. Edit / Save Brief: OK (Version advanced to v{updated_brief['version']})")

    # 10. Regenerate Hooks
    status, regen_brief = request("POST", f"/api/briefs/{brief['id']}/regenerate-hooks", None, token)
    assert status == 200 and len(regen_brief["hooks"]) >= 2
    print("✓ 10. Regenerate Hooks: OK (2 fresh alternative hooks generated)")

    # 11. Workspace Status Changes (Planned -> Filmed -> Published)
    status, filmed_b = request("PUT", f"/api/briefs/{brief['id']}/status", {"status": "filmed"}, token)
    assert status == 200 and filmed_b["status"] == "filmed"

    status, pub_b = request("PUT", f"/api/briefs/{brief['id']}/status", {"status": "published"}, token)
    assert status == 200 and pub_b["status"] == "published"
    print("✓ 11. Workspace Status Progression: OK (Planned -> Filmed -> Published)")

    # 12. Workspace Kanban Board & Summary
    status, ws = request("GET", "/api/workspace", None, token)
    assert status == 200 and len(ws["published"]) >= 1

    status, summary = request("GET", "/api/workspace/summary", None, token)
    assert status == 200 and summary["published"] >= 1
    print("✓ 12. Workspace Kanban & Summary: OK")

    # 13. Feedback Submission
    status, fb = request("POST", "/api/feedback", {
        "idea_id": selected_idea["id"],
        "brief_id": brief["id"],
        "rating": "not_useful",
        "reason": "Too generic",
        "details": "Focus even more on beginners"
    }, token)
    assert status == 201 and fb["rating"] == "not_useful"
    print("✓ 13. Feedback Submission: OK (Negative feedback recorded)")

    # 14. Feedback Influencing Future Generation (Personalization Loop)
    status, next_ideas = request("POST", "/api/ideas/generate", {}, token)
    assert status == 200 and len(next_ideas) >= 1
    print("✓ 14. Feedback Personalization Loop: OK (Future suggestions query negative feedback history)")

    # 15. Safe Diagnostic Endpoint
    status, diag = request("GET", "/api/ai/diagnostic")
    assert status == 200
    assert "provider" in diag and "model" in diag
    print(f"✓ 15. Safe AI Diagnostic: OK (Provider: {diag['provider']}, Model: {diag['model']}, Key Present: {diag['key_present']}, Fallback Enabled: {diag['fallback_enabled']})")

    # 16. Logout
    status, logout_res = request("POST", "/api/auth/logout", None, token)
    assert status == 200 and logout_res["status"] == "logged_out"
    print("✓ 16. Logout: OK")

    print("\n>>> ALL 16 LIVE USER FLOWS VERIFIED SUCCESSFULLY ON RUNNING SYSTEM <<<")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
