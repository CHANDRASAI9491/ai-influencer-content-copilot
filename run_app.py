"""
Influencer Help — AI Content Copilot
Single entry-point runner to start the production full-stack application.
"""
import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import uvicorn

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("==================================================================")
    print("  INFLUENCER HELP -- AI CONTENT COPILOT")
    print(f"  App Running at: http://127.0.0.1:{port}")
    print(f"  API Docs at:    http://127.0.0.1:{port}/docs")
    print(f"  Demo Creator:   Rahul (Telugu, Fitness, 30 min, Gym)")
    print("==================================================================")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
