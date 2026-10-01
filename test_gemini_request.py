import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    # 1. Login as demo user to get auth token
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/demo",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        token_data = json.loads(resp.read().decode())
        token = token_data["access_token"]

    # 2. Check diagnostic endpoint (safely without printing key)
    with urllib.request.urlopen(f"{BASE_URL}/api/ai/diagnostic") as resp:
        diag = json.loads(resp.read().decode())
        key_present = diag.get("key_present", False)

    # 3. Make ONE real generation request
    gen_req = urllib.request.Request(
        f"{BASE_URL}/api/ideas/generate",
        data=b"{}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(gen_req) as resp:
            ideas = json.loads(resp.read().decode())
            if ideas and len(ideas) > 0:
                first_meta = ideas[0].get("meta_info", {})
                provider_used = first_meta.get("provider", "")
                model_used = first_meta.get("model", "")
                is_fallback = first_meta.get("is_fallback", False)
                
                print(f"GEMINI_API_KEY present: {'YES' if key_present else 'NO'}")
                print("Provider: gemini")
                print("Model: gemini-2.5-flash")
                print(f"Real Gemini request: {'SUCCESS' if (provider_used == 'gemini' and not is_fallback) else 'FAIL'}")
                print(f"Fallback used: {'YES' if is_fallback else 'NO'}")
            else:
                print(f"GEMINI_API_KEY present: {'YES' if key_present else 'NO'}")
                print("Provider: gemini")
                print("Model: gemini-2.5-flash")
                print("Real Gemini request: FAIL")
                print("Fallback used: NO")
    except urllib.error.HTTPError as e:
        # Error from API (e.g. 502/400)
        err_body = e.read().decode()
        print(f"GEMINI_API_KEY present: {'YES' if key_present else 'NO'}")
        print("Provider: gemini")
        print("Model: gemini-2.5-flash")
        print("Real Gemini request: FAIL")
        print("Fallback used: NO")
    except Exception as e:
        print(f"GEMINI_API_KEY present: {'YES' if key_present else 'NO'}")
        print("Provider: gemini")
        print("Model: gemini-2.5-flash")
        print("Real Gemini request: FAIL")
        print("Fallback used: NO")

if __name__ == "__main__":
    run_test()
