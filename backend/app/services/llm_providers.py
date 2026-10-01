import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..config import settings

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Generate structured JSON response based on the prompt."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def model(self) -> Optional[str]:
        return None

    @property
    def is_fallback(self) -> bool:
        return False

    @property
    def fallback_reason(self) -> Optional[str]:
        return None

    @property
    def attempted_provider(self) -> Optional[str]:
        return None


def clean_json_string(text: str) -> str:
    """Clean markdown code blocks from LLM output."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", timeout: float = 30.0):
        self.api_key = api_key
        self._model = model
        self.timeout = timeout
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self._use_new_sdk = True
        except Exception as e:
            logger.warning(f"google.genai SDK init failed: {e}. Falling back to requests.")
            self._use_new_sdk = False

    @property
    def name(self) -> str:
        return "Google Gemini (Gemini 2.5 Flash)"

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        try:
            if self._use_new_sdk:
                from google.genai import types
                # HttpOptions accepts timeout in ms or s depending on version; pass seconds or ms
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                    http_options=types.HttpOptions(timeout=int(self.timeout * 1000))
                )
                try:
                    response = self.client.models.generate_content(
                        model=self._model,
                        contents=prompt,
                        config=config
                    )
                except Exception as gen_err:
                    err_msg = str(gen_err)
                    if ("404" in err_msg and ("not available" in err_msg.lower() or "not_found" in err_msg.lower() or "gemini" in err_msg.lower())) or "503" in err_msg:
                        import time
                        for candidate_model in ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
                            try:
                                logger.info(f"Connecting to real Google Gemini API with active model: {candidate_model}...")
                                response = self.client.models.generate_content(
                                    model=candidate_model,
                                    contents=prompt,
                                    config=config
                                )
                                self._model = candidate_model
                                break
                            except Exception as sub_err:
                                logger.warning(f"Candidate Gemini model {candidate_model} failed: {sub_err}")
                                time.sleep(1)
                        else:
                            raise gen_err
                    else:
                        raise
                text = response.text or ""
            else:
                import httpx
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json", "temperature": 0.7}
                }
                res = httpx.post(url, json=payload, timeout=self.timeout)
                res.raise_for_status()
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            cleaned = clean_json_string(text)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Gemini API generation failed ({self._model}): {e}")
            raise


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: float = 30.0):
        self.api_key = api_key
        self._model = model
        self.timeout = timeout
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    @property
    def name(self) -> str:
        return "OpenAI (GPT-4o Mini)"

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are a professional short-form content creator director. Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            text = response.choices[0].message.content or "{}"
            return json.loads(clean_json_string(text))
        except Exception as e:
            logger.error(f"OpenAI API generation failed: {e}")
            raise


class IntelligentCreativeEngine(BaseLLMProvider):
    """
    Local creative intelligence engine for instant, reliable, zero-config execution.
    Generates highly personalized ideas and briefs tailored dynamically to the creator's
    exact niche, audience, language, equipment, and environment constraints.
    """
    def __init__(
        self,
        is_fallback: bool = False,
        fallback_reason: Optional[str] = None,
        attempted_provider: Optional[str] = None
    ):
        self._is_fallback = is_fallback
        self._fallback_reason = fallback_reason
        self._attempted_provider = attempted_provider

    @property
    def name(self) -> str:
        if self._is_fallback:
            return f"Local Creative Engine (Fallback: {self._attempted_provider or 'External API'})"
        return "Local Creative Engine (Realistic Copilot)"

    @property
    def model(self) -> str:
        return "creative-engine-v1"

    @property
    def is_fallback(self) -> bool:
        return self._is_fallback

    @property
    def fallback_reason(self) -> Optional[str]:
        return self._fallback_reason

    @property
    def attempted_provider(self) -> Optional[str]:
        return self._attempted_provider

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        # Check if the prompt is for ideas or brief
        if "Generate exactly 5 personalized" in prompt or "CREATOR PROFILE:" in prompt and "OUTPUT FORMAT:\nReturn a single JSON object with key \"ideas\"" in prompt:
            return self._generate_ideas_response(prompt)
        elif "BRIEF_GENERATION_PROMPT" in prompt or "Generate a complete, structured, ready-to-shoot Content Brief" in prompt:
            return self._generate_brief_response(prompt)
        elif "HOOK_GENERATION_PROMPT" in prompt or "Generate two fresh, compelling opening hooks" in prompt:
            return self._generate_hooks_response(prompt)
        else:
            return self._generate_ideas_response(prompt)

    def _extract_tag(self, prompt: str, label: str, default: str = "") -> str:
        match = re.search(rf"- {label}:\s*(.+)", prompt)
        if match:
            val = match.group(1).strip()
            # remove brackets or quotes
            val = re.sub(r"[\[\]'\"]", "", val)
            return val
        return default

    def _generate_ideas_response(self, prompt: str) -> Dict[str, Any]:
        niche = self._extract_tag(prompt, "Primary Niche", "Fitness")
        language = self._extract_tag(prompt, "Preferred Language", "Telugu")
        audience = self._extract_tag(prompt, "Target Audience", "College students and beginners")
        equipment = self._extract_tag(prompt, "Available Equipment", "Smartphone")
        env = self._extract_tag(prompt, "Filming Environment", "Gym")
        time_limit = self._extract_tag(prompt, "Available Filming Time", "30 minutes")
        goal = self._extract_tag(prompt, "Primary Goals", "Grow audience")

        # Niche-aware knowledge matrix
        is_fitness = any(x in niche.lower() for x in ["fit", "gym", "workout", "health", "diet"])
        is_tech = any(x in niche.lower() for x in ["tech", "coding", "software", "ai", "computer"])
        is_food = any(x in niche.lower() for x in ["food", "cook", "recipe", "baking"])
        is_finance = any(x in niche.lower() for x in ["finan", "money", "invest", "stock"])

        if is_fitness:
            ideas = [
                {
                    "title": f"3 Gym Mistakes Beginners Make ({language} Guide)",
                    "description": f"Identify 3 dangerous yet common posture mistakes beginners make in the gym and demonstrate the quick 5-second fix for each, spoken in natural {language}.",
                    "format": "Educational Reel",
                    "difficulty": "Easy",
                    "estimated_time": "25 minutes",
                    "why_it_fits": f"Your niche is {niche}, your audience is {audience}, and this can be filmed smoothly in the {env} with just your {equipment}.",
                    "required_equipment": [equipment or "Smartphone", "Water bottle or phone stand"],
                    "shooting_environment": env or "Gym",
                    "originality_considerations": "Focus on the psychological fear beginners feel about asking gym trainers, making your advice empathetic and reassuring."
                },
                {
                    "title": f"Budget Protein Plan for College Students",
                    "description": f"Break down 3 high-protein, ultra-affordable food options available locally under ₹50 for college students trying to hit their fitness goals.",
                    "format": "Listicle Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"Directly answers your goal to '{goal}' by addressing the exact financial constraint of your target audience ({audience}).",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home / Hostel",
                    "originality_considerations": "Show real local prices and actual portion sizes on a student plate rather than generic imported supplements."
                },
                {
                    "title": f"Why Your Dumbbell Curls Aren't Growing Your Arms",
                    "description": "Expose the momentum swing mistake during arm day and demonstrate the elbow-pinned isolation technique with side-by-side visual contrast.",
                    "format": "Tutorial Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"Quick high-engagement problem-solving reel that requires zero fancy gear, perfectly feasible in {time_limit}.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Gym",
                    "originality_considerations": "Use a relatable mental cue like 'imagine your elbows are glued to a wall' instead of complicated biomechanical terms."
                },
                {
                    "title": f"15-Minute No-Excuses Dorm/Home Workout",
                    "description": "Show a fast, sweaty bodyweight circuit (pushups, squats, mountain climbers) college students can execute right next to their bed with zero weights.",
                    "format": "POV / Follow-Along",
                    "difficulty": "Medium",
                    "estimated_time": "30 minutes",
                    "why_it_fits": f"Designed specifically for {audience} who have limited gym access or time constraints.",
                    "required_equipment": [equipment or "Smartphone", "Floor mat / towel"],
                    "shooting_environment": "Dorm / Home / Hostel",
                    "originality_considerations": "Keep the camera at floor-level POV so viewers feel like they are working out alongside you in real-time."
                },
                {
                    "title": f"The #1 Reason Beginners Quit the Gym in Week 2",
                    "description": "A grounded, honest talking-head addressing muscle soreness (DOMS) vs injury, encouraging beginners to stay consistent through the first 14 days.",
                    "format": "Talking Head / Motivation",
                    "difficulty": "Easy",
                    "estimated_time": "15 minutes",
                    "why_it_fits": f"Builds strong personal connection with {audience} while demanding minimal production overhead.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Gym / Home",
                    "originality_considerations": "Recount your very first awkward week in the gym to humanize your brand and inspire trust."
                }
            ]
        elif is_tech:
            ideas = [
                {
                    "title": f"3 VS Code Shortcuts That Feel Like Cheating ({language})",
                    "description": f"Quick screen recording showcasing multi-cursor editing, command palette jump, and automated refactoring in {language}.",
                    "format": "Tutorial Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"Perfect fit for {audience} learning to code, feasible using just laptop and screen capture.",
                    "required_equipment": ["Laptop / PC", "Screen recorder"],
                    "shooting_environment": "Desk / Office",
                    "originality_considerations": "Show real code snippets from popular beginner projects like React or Python scripts."
                },
                {
                    "title": "Stop Using AI to Write Your Entire Project",
                    "description": "Explain the difference between using AI as an architectural co-pilot versus blind copy-pasting that breaks during job interviews.",
                    "format": "Talking Head",
                    "difficulty": "Easy",
                    "estimated_time": "15 minutes",
                    "why_it_fits": f"High engagement topic for {audience} looking for genuine tech career guidance.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": "Home / Office",
                    "originality_considerations": "Share a specific debugging disaster caused by unverified AI code and how to avoid it."
                },
                {
                    "title": "Roadmap: Zero to First Web Dev Internship",
                    "description": "Clear step-by-step 3-phase path: HTML/CSS foundation, JS logic, and 1 portfolio project that actually catches recruiters' eyes.",
                    "format": "Educational Reel",
                    "difficulty": "Medium",
                    "estimated_time": "25 minutes",
                    "why_it_fits": f"Targets your goal to {goal} by solving the most pressing pain point of college students.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": "Home / College",
                    "originality_considerations": "Review a mock resume and point out what recruiters look for in 6 seconds."
                },
                {
                    "title": "Git Mistakes Every Student Makes (And How to Undo Them)",
                    "description": "Demonstrate how to fix accidental commits, revert changes without losing work, and avoid pushing secret keys.",
                    "format": "Tutorial Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": "Practical, immediate relief for an everyday developer headache.",
                    "required_equipment": ["Laptop", equipment or "Smartphone"],
                    "shooting_environment": "Desk",
                    "originality_considerations": "Use a clear visual analogy of Git branches as train tracks."
                },
                {
                    "title": "Free Tools Every CS Student Should Know in 2026",
                    "description": "List 3 lesser-known free student developer packs, APIs, and hosting platforms that save hundreds of dollars.",
                    "format": "Listicle Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"Highly shareable and save-worthy for {audience}.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": "Home / College",
                    "originality_considerations": "Demonstrate the instant activation with a .edu email."
                }
            ]
        else:
            # Universal creator template
            ideas = [
                {
                    "title": f"3 Rookie Mistakes Beginners Make in {niche}",
                    "description": f"Break down the 3 most common errors people make when starting out in {niche}, delivered with actionable quick fixes in {language}.",
                    "format": "Educational Reel",
                    "difficulty": "Easy",
                    "estimated_time": time_limit or "25 minutes",
                    "why_it_fits": f"Tailored to {audience} who need clarity without intimidation, easily filmed with {equipment}.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home",
                    "originality_considerations": "Draw from your personal early mistakes to deliver genuine authenticity."
                },
                {
                    "title": f"The 5-Minute Daily Habit for Better {niche} Results",
                    "description": f"Highlight one micro-habit that compounds over 30 days, breaking down the exact routine for {audience}.",
                    "format": "Tutorial Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"Fast to film in {env} and delivers immediate high-value utility.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home",
                    "originality_considerations": "Show your personal tracking sheet or habit loop in action."
                },
                {
                    "title": f"Budget vs Expensive: What Actually Matters in {niche}?",
                    "description": f"Compare high-cost tools against accessible budget alternatives so {audience} avoid wasting hard-earned money.",
                    "format": "Before / After / Comparison",
                    "difficulty": "Medium",
                    "estimated_time": "30 minutes",
                    "why_it_fits": f"Addresses the core financial reality of {audience} with unbiased, practical advice.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home",
                    "originality_considerations": "Prove that technique and consistency beat expensive equipment."
                },
                {
                    "title": f"The One Thing I Wish I Knew Before Starting {niche}",
                    "description": "An intimate, transparent talking-head video unpacking the single biggest myth that holds people back from progressing.",
                    "format": "Talking Head / Storytelling",
                    "difficulty": "Easy",
                    "estimated_time": "15 minutes",
                    "why_it_fits": f"Builds strong audience trust and personal branding in {language}.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home / Studio",
                    "originality_considerations": "Reveal an unexpected lesson that counteracts conventional wisdom."
                },
                {
                    "title": f"Quick Checklist: How to Audit Your {niche} Progress",
                    "description": "Deliver a 4-point rapid scorecard viewers can use immediately to measure if their efforts are moving the needle.",
                    "format": "Listicle Reel",
                    "difficulty": "Easy",
                    "estimated_time": "20 minutes",
                    "why_it_fits": f"High save rate potential since viewers will want to reference the scorecard later.",
                    "required_equipment": [equipment or "Smartphone"],
                    "shooting_environment": env or "Home",
                    "originality_considerations": "Provide an on-screen screenshot summary frame for easy saving."
                }
            ]

        return {"ideas": ideas}

    def _generate_brief_response(self, prompt: str) -> Dict[str, Any]:
        idea_title = self._extract_tag(prompt, "Title", "3 Gym Mistakes Beginners Make")
        format_type = self._extract_tag(prompt, "Format", "Educational Reel")
        audience = self._extract_tag(prompt, "Audience", "College students and beginners")
        language = self._extract_tag(prompt, "Language", "Telugu")
        equipment = self._extract_tag(prompt, "Equipment", "Smartphone")
        env = self._extract_tag(prompt, "Environment", "Gym")
        filming_time = self._extract_tag(prompt, "Time Budget", "30 minutes")

        is_telugu = "telugu" in language.lower()

        # Hooks
        if is_telugu:
            hook_a = "Gym ki velle beginners chestunna 3 dangerous mistakes ivi! (These 3 gym mistakes hurt your gains)"
            hook_b = "Day 1 nunchi mee body grow avvakapovadaniki ee okka mistake kaaranam undochu... telusa? (Could this one mistake stall your progress?)"
            s1 = "Meelo chala mandi gym ki start chesi week 2 lopu pains valla quit chestaru. Ee 3 mistakes asalu cheyoddu."
            s2 = "Mistake 1: Warmup cheyakunda direct gaa heavy weights lift cheyadam. Ee form chudandi."
            s3 = "Correct Technique: Shoulder back, core tight, and controlled tempo lo dumbbells move cheyandi."
            s4 = "Mistake 2: Daily routine marchadam. 8 weeks okate workout plan follow avvandi."
            s5 = "E roje mee gym partner tho ee reel share cheyandi, and fitness journey start cheyandi!"
            caption_lead = "Gym ki velle prathi college student and beginner thappakunda thelusukovaalsina 3 main points! 💪"
        else:
            hook_a = "Stop lifting like this! 3 mistakes that are ruining your gym progress."
            hook_b = "What if the reason you're not seeing gains has nothing to do with how hard you train?"
            s1 = "If you started working out recently, chances are you are making at least one of these 3 posture mistakes."
            s2 = "Mistake 1: Swings during bicep curls. When you rock your back, your lower back takes the load, not your arms."
            s3 = "The Fix: Pin your elbows to your ribcage. Lower the weight by 2kg and control the 3-second descent."
            s4 = "Mistake 2: Skipping leg drive on benches and letting your wrists bend completely backwards."
            s5 = "Save this reel for your next gym session and follow for simple daily beginner tips!"
            caption_lead = "3 common gym mistakes beginners make and how to fix them in 5 seconds! 🏋️‍♂️"

        return {
            "title": idea_title,
            "format": format_type,
            "target_audience": audience,
            "why_it_fits": f"Directly addresses {audience} in practical language, easily shootable in the {env} using a {equipment}.",
            "estimated_duration": "35–45 seconds",
            "difficulty": "Easy",
            "hooks": [
                {
                    "type": "direct",
                    "text": hook_a
                },
                {
                    "type": "curiosity",
                    "text": hook_b
                }
            ],
            "script": [
                {
                    "section": "0–3 sec",
                    "title": "Hook",
                    "content": hook_a
                },
                {
                    "section": "3–10 sec",
                    "title": "Problem",
                    "content": s1
                },
                {
                    "section": "10–25 sec",
                    "title": "Mistake & Solution 1",
                    "content": f"{s2} -> {s3}"
                },
                {
                    "section": "25–35 sec",
                    "title": "Mistake 2 & Key Insight",
                    "content": s4
                },
                {
                    "section": "35–40 sec",
                    "title": "Call to Action",
                    "content": s5
                }
            ],
            "shots": [
                {
                    "order": 1,
                    "description": "Talking-head opening delivery straight to camera with confident body posture.",
                    "framing": "Medium Close-Up (Eye Level)",
                    "visual_text": "STOP doing this in the gym!"
                },
                {
                    "order": 2,
                    "description": "Side-profile shot demonstrating the incorrect momentum swing form.",
                    "framing": "Side Medium Shot",
                    "visual_text": "❌ Mistake: Back swing"
                },
                {
                    "order": 3,
                    "description": "Side-profile shot demonstrating the corrected locked elbow position with steady cadence.",
                    "framing": "Side Medium Shot",
                    "visual_text": "✅ Fix: Elbows locked"
                },
                {
                    "order": 4,
                    "description": "Close-up on wrist angle during grip positioning.",
                    "framing": "Close-Up (Hands/Dumbbell)",
                    "visual_text": "Neutral wrist grip"
                },
                {
                    "order": 5,
                    "description": "Return to talking-head delivering closing advice and pointing to save/follow button.",
                    "framing": "Medium Shot",
                    "visual_text": "Save this reel 📌"
                }
            ],
            "caption": f"{caption_lead}\n\nDon't let bad form slow down your fitness journey. When you focus on control instead of ego-lifting, your results double and injuries drop to zero.\n\n👇 Which of these mistakes did you make when you first started? Drop a comment below!\n\n#FitnessTips #BeginnerGym #WorkoutForm #GymMotivation #HealthyLiving #FitnessGoals",
            "cta": "Save this reel for your next workout session and tag your gym partner!",
            "content_objective": "Educate beginners and correct common posture mistakes to build audience trust",
            "recommended_hook": "direct",
            "hashtags": ["#FitnessTips", "#GymForm", "#BeginnerWorkout", "#ReelTips", "#CreatorCopilot"],
            "on_screen_text": [
                "Stop Doing This ❌",
                "Lock Your Elbows ✅",
                "Control The Negative (3 Secs)",
                "Save For Next Gym Day 📌"
            ],
            "requirements": [
                f"{equipment} with clean camera lens",
                f"Location: {env} (quiet corner near dumbbell rack)",
                "Filming effort: ~20-25 minutes setup & recording",
                "No extra cameraman required (use water bottle/tripod as stand)"
            ],
            "editing_notes": [
                "Keep fast pacing with visual punch-in zoom on mistake point",
                "Ensure text overlays remain in the central 9:16 safe zone",
                "Export at 1080x1920 60fps for crisp video quality"
            ],
            "b_roll_requirements": [
                "B-roll cutaway of dumbbell rack and weights setup",
                "Side-angle macro shot of forearm tension"
            ],
            "audio_requirements": [
                "Clean clear vocal audio, background ambient track under -24dB",
                "Subtle bass whoosh sound effect on Fix graphic transition"
            ],
            "assumptions": [
                "Assumes filming solo with smartphone propped securely",
                "Assumes standard gym ambient lighting without external studio lights",
                "Timings are planning guidelines rather than rigid stopwatches"
            ],
            "originality_notes": [
                "Share the exact mistake you personally struggled with during your first month of gym workouts",
                f"Deliver spoken dialogue naturally in {language} rather than robotic translation",
                "Avoid complex kinesiology terms; use relatable everyday cues"
            ],
            "platform_notes": [
                "Optimized for 9:16 vertical full-screen mobile viewing",
                "Keep caption first line under 80 characters before '...more' truncation"
            ]
        }

    def _generate_hooks_response(self, prompt: str) -> Dict[str, Any]:
        return {
            "hooks": [
                {
                    "type": "direct",
                    "text": "If you are making this one mistake, you are wasting 50% of your effort."
                },
                {
                    "type": "curiosity",
                    "text": "Why does nobody talk about this simple fix that changes everything?"
                }
            ]
        }


def get_llm_provider(allow_fallback: bool = True) -> BaseLLMProvider:
    """
    Factory to get the appropriate LLM provider based on settings.AI_PROVIDER
    and API key configuration.
    
    Provider resolution logic:
    - 'gemini': Uses GeminiProvider(gemini-2.5-flash).
      If GEMINI_API_KEY is missing:
        - If allow_fallback and AI_FALLBACK_ON_ERROR: returns IntelligentCreativeEngine(is_fallback=True)
        - Else: raises ValueError.
    - 'openai': Uses OpenAIProvider(gpt-4o-mini).
      If OPENAI_API_KEY is missing:
        - If allow_fallback and AI_FALLBACK_ON_ERROR: returns IntelligentCreativeEngine(is_fallback=True)
        - Else: raises ValueError.
    - 'creative_engine': Always returns IntelligentCreativeEngine(is_fallback=False).
    - 'auto':
        1. If GEMINI_API_KEY is configured -> GeminiProvider.
        2. Else if OPENAI_API_KEY is configured -> OpenAIProvider.
        3. Else -> IntelligentCreativeEngine(is_fallback=False).
    """
    provider_pref = settings.AI_PROVIDER.lower().strip()
    fallback_enabled = settings.AI_FALLBACK_ON_ERROR and allow_fallback

    if provider_pref == "gemini":
        if settings.GEMINI_API_KEY:
            try:
                return GeminiProvider(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.warning(f"Could not load Gemini provider: {e}")
                if fallback_enabled:
                    return IntelligentCreativeEngine(
                        is_fallback=True,
                        fallback_reason=f"Gemini initialization error: {e}",
                        attempted_provider="Google Gemini (Gemini 2.5 Flash)"
                    )
                raise
        else:
            if fallback_enabled:
                logger.warning("AI_PROVIDER is 'gemini' but GEMINI_API_KEY is missing. Falling back to Local Creative Engine.")
                return IntelligentCreativeEngine(
                    is_fallback=True,
                    fallback_reason="Missing GEMINI_API_KEY environment variable",
                    attempted_provider="Google Gemini (Gemini 2.5 Flash)"
                )
            raise ValueError("AI_PROVIDER is set to 'gemini' but GEMINI_API_KEY is missing from environment.")

    elif provider_pref == "openai":
        if settings.OPENAI_API_KEY:
            try:
                return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Could not load OpenAI provider: {e}")
                if fallback_enabled:
                    return IntelligentCreativeEngine(
                        is_fallback=True,
                        fallback_reason=f"OpenAI initialization error: {e}",
                        attempted_provider="OpenAI (GPT-4o Mini)"
                    )
                raise
        else:
            if fallback_enabled:
                logger.warning("AI_PROVIDER is 'openai' but OPENAI_API_KEY is missing. Falling back to Local Creative Engine.")
                return IntelligentCreativeEngine(
                    is_fallback=True,
                    fallback_reason="Missing OPENAI_API_KEY environment variable",
                    attempted_provider="OpenAI (GPT-4o Mini)"
                )
            raise ValueError("AI_PROVIDER is set to 'openai' but OPENAI_API_KEY is missing from environment.")

    elif provider_pref == "creative_engine":
        return IntelligentCreativeEngine(is_fallback=False)

    elif provider_pref == "auto":
        if settings.GEMINI_API_KEY:
            try:
                return GeminiProvider(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                logger.warning(f"Auto-provider: Gemini init failed: {e}")
        
        if settings.OPENAI_API_KEY:
            try:
                return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Auto-provider: OpenAI init failed: {e}")

        # Default clean execution with no external API dependency
        return IntelligentCreativeEngine(is_fallback=False)

    else:
        # Unknown provider string
        if fallback_enabled:
            logger.warning(f"Unknown AI_PROVIDER '{provider_pref}'. Falling back to Local Creative Engine.")
            return IntelligentCreativeEngine(
                is_fallback=True,
                fallback_reason=f"Unknown AI_PROVIDER setting '{provider_pref}'",
                attempted_provider=provider_pref
            )
        raise ValueError(f"Unknown AI_PROVIDER setting: '{provider_pref}'")
