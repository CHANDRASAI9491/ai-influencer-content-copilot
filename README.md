# Influencer Help — AI Content Copilot

> **“Tell us what kind of creator you are and what you have available. We turn that into content you can actually create.”**

**Influencer Help — AI Content Copilot** is a production-ready, full-stack MVP designed specifically for short-form video creators. Influencers often know they need to create content but struggle to consistently bridge the gap between their niche, audience, available filming time, and equipment into concrete, shootable reels.

This application bridges:
**Creator need → Content idea → Reel concept → Script → Shot list → Caption/CTA → Save → Create → Feedback**

---

## 📸 Core Product Highlights

- **No Generic Chatbots**: Unlike conversational bots that output freeform blocks of text, Copilot provides structured, shootable production briefs with timed scripts, camera framing, and props.
- **Two-Hook Feature**: Every brief provides **Hook A (Direct)** for immediate attention and **Hook B (Curiosity)** without false virality claims.
- **Ordered Shot Lists**: Complete visual shot lists with camera framing cues (Medium Close-Up, Side Angle, POV) and text overlays.
- **Timed Script Breakdown**: Segmented dialogue (0–3s, 3–10s, 10–25s, 25–35s, 35–40s) tailored to planning cadence.
- **Private Workspace Pipeline**: Track content across **Ideas**, **Planned**, **Filmed**, **Published**, and **Archived** stages (with self-reported status disclaimer).
- **Creator Feedback System**: 👍 Useful / 👎 Not useful with categorized reasons that guide future recommendations without automatic unverified retraining.
- **1-Click Demo Mode (Rahul)**: Pre-seeded Telugu fitness creator profile (College students, 30 min, Smartphone, Gym) ready for immediate evaluation.

---

## 🏗️ Architecture & Technology Stack

```
Frontend (React 19 + Vite + Vanilla CSS Glassmorphism + Lucide Icons)
      │
      ▼  (HTTP / JSON API & Static Delivery)
Backend API (FastAPI + Pydantic v2 + JWT Security)
      │
      ▼
Application Service Layer (AIService Pipeline + Input Sanitization + Prompt Versioning)
      │
      ├──► Database (SQLAlchemy ORM: SQLite default / PostgreSQL ready)
      └──► AI Provider Layer (Google Gemini / OpenAI / Intelligent Creative Engine)
```

- **Backend**: Python 3.14, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, HTTPX, Pytest.
- **Frontend**: React 19, Vite, Vanilla CSS Design System with mobile-first responsive layout, dark mode, glassmorphism, and Outfit / Plus Jakarta Sans typography.
- **AI Service Layer**: Versioned prompts (`idea_generation_v1`, `brief_generation_v1`, `hook_generation_v1`, `caption_generation_v1`), strict Pydantic JSON schema validation, and safety filters that eliminate unsupported virality claims.

---

## 🗄️ Database Schema

| Table | Description | Key Fields |
|---|---|---|
| `users` | Creator credentials & auth | `id`, `email`, `hashed_password`, `display_name`, `status`, `created_at` |
| `creator_profiles` | Niche, audience & equipment | `id`, `user_id`, `creator_type`, `niches`, `languages`, `target_audience`, `goals`, `formats`, `equipment`, `filming_time`, `environment` |
| `content_ideas` | Generated & saved reel concepts | `id`, `user_id`, `title`, `description`, `format`, `difficulty`, `estimated_time`, `why_it_fits`, `status`, `meta_info` |
| `content_briefs` | Complete shootable briefs | `id`, `user_id`, `idea_id`, `title`, `selected_hook_type`, `hooks`, `script`, `shots`, `caption`, `cta`, `requirements`, `assumptions`, `originality_notes`, `status`, `version` |
| `feedback` | Creator ratings & reasons | `id`, `user_id`, `idea_id`, `brief_id`, `rating`, `reason`, `details`, `created_at` |

---

## 🛣️ API Endpoints

### Authentication
- `POST /api/auth/register` — Register a new creator account.
- `POST /api/auth/login` — Sign in and receive JWT token.
- `POST /api/auth/demo` — 1-click instant login as demo creator Rahul.
- `GET  /api/auth/me` — Current authenticated user profile.

### Creator Profile
- `GET  /api/profile` — Fetch active creator preferences.
- `PUT  /api/profile` — Update niches, languages, equipment, filming time, or environment.
- `POST /api/profile/reset-demo` — Reset to Rahul demo creator specifications.

### Content Ideas
- `POST /api/ideas/generate` — Generate 5 personalized, constraint-aware ideas.
- `GET  /api/ideas` — List user's ideas (supports `status_filter`).
- `GET  /api/ideas/{id}` — Get single idea detail with strict ownership verification.
- `PATCH /api/ideas/{id}/select` — Select idea for brief creation.
- `DELETE /api/ideas/{id}` — Delete idea.

### Content Briefs
- `POST /api/briefs/generate` — Generate complete structured reel brief.
- `GET  /api/briefs` — List creator's briefs (filter by planned, filmed, published, archived).
- `GET  /api/briefs/{id}` — Retrieve full brief studio data.
- `PUT  /api/briefs/{id}` — Edit title, hooks, script segments, shots, caption, or CTA with version conflict protection.
- `PATCH /api/briefs/{id}/status` — Update stage (`planned`, `filmed`, `published`, `archived`).
- `POST /api/briefs/{id}/regenerate-hooks` — Regenerate fresh direct & curiosity hooks.
- `DELETE /api/briefs/{id}` — Delete brief.

### Workspace & Feedback
- `GET  /api/workspace/summary` — Stage counts with self-reported disclaimer.
- `POST /api/feedback` — Submit thumbs up/down and categorized reasons.
- `GET  /api/feedback` — List past feedback entries.

---

## 🧪 Automated Test Suite

Run all automated unit and integration tests:

```bash
python -m pytest backend/tests -v
```

Results:
```text
backend/tests/test_auth_profile.py::test_register_and_profile_flow PASSED [16%]
backend/tests/test_auth_profile.py::test_demo_login_and_reset PASSED     [33%]
backend/tests/test_ideas_briefs.py::test_ideas_and_briefs_lifecycle PASSED [50%]
backend/tests/test_security_feedback.py::test_security_multi_tenant_isolation PASSED [66%]
backend/tests/test_security_feedback.py::test_feedback_system PASSED     [83%]
backend/tests/test_user_journey.py::test_complete_mvp_user_journey PASSED [100%]
============================== 6 passed in 3.63s ==============================
```

---

## 🚀 Quickstart & Local Setup

### 1. Requirements
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node v24.15.0)

### 2. Run the Full-Stack Application
In the project root directory, run:

```bash
python run_app.py
```

Then open:
- **Application UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Environment Variables (`.env`)
```ini
ENVIRONMENT=development               # development, test, or production
# In production, SECRET_KEY is REQUIRED (at least 32 characters).
# Generate using: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=

DATABASE_URL=sqlite:///./copilot.db   # Or postgresql://user:password@localhost/copilot_db
AI_PROVIDER=auto                      # auto, gemini, openai, or creative_engine
GEMINI_API_KEY=your_gemini_key_here   # Optional: uses Gemini 2.5 Flash
OPENAI_API_KEY=your_openai_key_here   # Optional: uses GPT-4o-mini
```
*(In development, an ephemeral cryptographically strong secret is generated automatically if omitted. In production, a secure `SECRET_KEY` is strictly enforced.)*

---

## 📱 Step-by-Step User Journey

1. **Landing Page**: Value proposition and production bridge explanation. Click **"Try as Rahul (Telugu Fitness Demo)"** or **"Start Creating Now"**.
2. **Onboarding / Profile**: Choose niches (Fitness, Tech, Cooking, Finance, etc.), languages, audience, gear, and time limits.
3. **Creator Dashboard**: View **"What do you want to create today?"** with active profile banner and 5 tailored idea cards.
4. **Inspect Idea**: Review concept, why it fits, required gear, environment, and originality tips. Click **"Create My Reel"**.
5. **AI Content Brief Studio**:
   - Choose between **Hook A (Direct)** and **Hook B (Curiosity)**.
   - Edit the **Timed Script** (0-3s, 3-10s, 10-25s, 25-35s, 35-40s).
   - Review and customize the **Ordered Shot List** with camera framing cues.
   - Edit the **Caption** & **CTA**.
   - Check **Practical Requirements**, **Assumptions**, and **Originality Notes**.
   - Click **Save Brief** or **Copy Script**.
6. **Workspace**: Move content from **Planned** to **Filmed** and **Published**.
7. **Feedback**: Rate whether the generation was useful (👍 / 👎) with categorized reasons to tune future suggestions.
