from sqlalchemy.orm import Session
from .models import User, CreatorProfile, ContentIdea, ContentBrief, Feedback
from .auth import hash_password

DEMO_USER_EMAIL = "rahul.demo@influencercopilot.local"

def ensure_demo_user(db: Session) -> User:
    """
    Ensure the official demo creator (Rahul) exists in the database
    with his exact specified context:
    - Name: Rahul
    - Niche: Fitness (Secondary: Nutrition, Motivation)
    - Language: Telugu
    - Audience: College students and beginners
    - Goal: Grow audience
    - Equipment: Smartphone
    - Time: 30 minutes
    - Location: Gym
    """
    user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
    if not user:
        user = User(
            email=DEMO_USER_EMAIL,
            hashed_password=hash_password("DemoCreator2026!"),
            display_name="Rahul",
            status="active"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Check profile
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == user.id).first()
    if not profile:
        profile = CreatorProfile(
            user_id=user.id,
            creator_type="Aspiring Influencer",
            niches=["Fitness"],
            secondary_niches=["Nutrition", "Motivation"],
            languages=["Telugu", "English"],
            target_audience="College students and beginners",
            broad_location="Hyderabad, India",
            goals=["Grow audience", "Educate"],
            formats=["Educational", "Tutorial", "POV"],
            equipment=["Smartphone"],
            filming_time="30 minutes",
            environment="Gym"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Seed initial ideas if user has none
    ideas_count = db.query(ContentIdea).filter(ContentIdea.user_id == user.id).count()
    if ideas_count == 0:
        demo_ideas = [
            ContentIdea(
                user_id=user.id,
                title="3 Gym Mistakes Beginners Make (Telugu Guide)",
                description="Common form errors on dumbbell curls, squats, and bench presses, explained simply in conversational Telugu for beginners.",
                format="Educational Reel",
                difficulty="Easy",
                estimated_time="25 minutes",
                why_it_fits="Your niche is Fitness, your audience is beginners, and this can be filmed solo with your Smartphone in the gym.",
                status="selected",
                meta_info={
                    "required_equipment": ["Smartphone"],
                    "shooting_environment": "Gym",
                    "originality_considerations": "Emphasize empathy for beginner intimidation rather than harsh criticism.",
                    "is_demo_seed": True
                }
            ),
            ContentIdea(
                user_id=user.id,
                title="₹50 Daily Protein Plan for College Hostelers",
                description="3 high-protein pocket-friendly foods available in student messes and local markets that hit 25g+ protein.",
                format="Listicle Reel",
                difficulty="Easy",
                estimated_time="20 minutes",
                why_it_fits="Directly tackles the budget crunch of your target audience (college students).",
                status="suggested",
                meta_info={
                    "required_equipment": ["Smartphone"],
                    "shooting_environment": "Hostel / Room",
                    "originality_considerations": "Show real local prices and actual street vendors.",
                    "is_demo_seed": True
                }
            ),
            ContentIdea(
                user_id=user.id,
                title="Why Your Arms Aren't Growing (Stop Back Swinging)",
                description="Side-by-side visual of momentum cheating vs elbow-pinned isolation curl.",
                format="Tutorial Reel",
                difficulty="Easy",
                estimated_time="20 minutes",
                why_it_fits="Quick, high-retention reel feasible in 20 minutes between workout sets.",
                status="suggested",
                meta_info={
                    "required_equipment": ["Smartphone"],
                    "shooting_environment": "Gym",
                    "originality_considerations": "Use the cue 'glue your elbows to an imaginary wall'.",
                    "is_demo_seed": True
                }
            ),
            ContentIdea(
                user_id=user.id,
                title="15-Min No-Equipment Hostel Room Workout",
                description="Sweaty 3-exercise routine students can do beside their bed without any gym membership.",
                format="POV / Follow-Along",
                difficulty="Medium",
                estimated_time="30 minutes",
                why_it_fits="Helps audience stay consistent during exam weeks when gym trips are impossible.",
                status="suggested",
                meta_info={
                    "required_equipment": ["Smartphone"],
                    "shooting_environment": "Hostel / Home",
                    "originality_considerations": "Shoot from an authentic floor-angle POV.",
                    "is_demo_seed": True
                }
            ),
            ContentIdea(
                user_id=user.id,
                title="The #1 Reason Beginners Quit Gym in Week 2",
                description="Explaining muscle soreness (DOMS) vs real injury, reassuring beginners that soreness fades.",
                format="Talking Head",
                difficulty="Easy",
                estimated_time="15 minutes",
                why_it_fits="Builds deep trust and emotional rapport with your beginner followers.",
                status="suggested",
                meta_info={
                    "required_equipment": ["Smartphone"],
                    "shooting_environment": "Gym",
                    "originality_considerations": "Share your own awkward first week experience.",
                    "is_demo_seed": True
                }
            )
        ]
        for idea in demo_ideas:
            db.add(idea)
        db.commit()

        # Seed 1 complete brief for the first idea so the user can immediately explore an editable brief
        first_idea = db.query(ContentIdea).filter(ContentIdea.user_id == user.id).first()
        if first_idea:
            demo_brief = ContentBrief(
                user_id=user.id,
                idea_id=first_idea.id,
                title=first_idea.title,
                selected_hook_type="direct",
                hooks=[
                    {
                        "type": "direct",
                        "text": "Gym ki velle beginners chestunna 3 dangerous mistakes ivi! (Stop making these 3 gym mistakes!)"
                    },
                    {
                        "type": "curiosity",
                        "text": "Day 1 nunchi mee body grow avvakapovadaniki ee okka mistake kaaranam undochu... telusa? (Could this one mistake stall your progress?)"
                    }
                ],
                script=[
                    {
                        "section": "0–3 sec",
                        "title": "Hook",
                        "content": "Gym ki velle beginners chestunna 3 dangerous mistakes ivi! Meekuda telikunda chestunnaremo chusukondi."
                    },
                    {
                        "section": "3–10 sec",
                        "title": "Problem",
                        "content": "Chala mandi gym join ayyi week 2 lo severe body pains valla aapestaru. But form correct unte pain raadu, muscle grow avtundi."
                    },
                    {
                        "section": "10–25 sec",
                        "title": "Mistake & Solution 1",
                        "content": "Mistake 1: Dumbbell curls chestunnappudu back swing cheyadam. Fix: Elbows ni ribcage ki lock chesi, 3-second negative descent tho lift cheyandi."
                    },
                    {
                        "section": "25–35 sec",
                        "title": "Mistake 2 & Key Insight",
                        "content": "Mistake 2: Daily routine change cheyadam. At least 6-8 weeks okate workout plan follow avvandi. Consistency beats hype."
                    },
                    {
                        "section": "35–40 sec",
                        "title": "Call to Action",
                        "content": "Ee reel ni mee gym partner tho share cheyandi, and daily beginner fitness tips kosam follow cheyandi!"
                    }
                ],
                shots=[
                    {
                        "order": 1,
                        "description": "Talking-head opening delivery straight to camera with confident, friendly posture.",
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
                caption="Gym ki velle prathi college student and beginner thappakunda thelusukovaalsina 3 main points! 💪\n\nDon't let bad form slow down your fitness journey. When you focus on control instead of ego-lifting, your results double and injuries drop to zero.\n\n👇 Which of these mistakes did you make when you first started? Drop a comment below!\n\n#FitnessTips #BeginnerGym #TeluguFitness #WorkoutForm #GymMotivation #HealthyLiving",
                cta="Save this reel for your next workout session and tag your gym partner!",
                on_screen_text=[
                    "Stop Doing This ❌",
                    "Lock Your Elbows ✅",
                    "Control The Negative (3 Secs)",
                    "Save For Next Gym Day 📌"
                ],
                requirements=[
                    "Smartphone with clean camera lens",
                    "Location: Gym (quiet corner near dumbbell rack)",
                    "Filming effort: ~20-25 minutes setup & recording",
                    "No extra cameraman required (use water bottle/tripod as stand)"
                ],
                assumptions=[
                    "Assumes filming solo with smartphone propped securely",
                    "Assumes standard gym ambient lighting without external studio lights",
                    "Timings are planning guidelines rather than rigid stopwatches"
                ],
                originality_notes=[
                    "Share the exact mistake you personally struggled with during your first month of gym workouts",
                    "Deliver spoken dialogue naturally in Telugu rather than robotic translation",
                    "Avoid complex kinesiology terms; use relatable everyday cues"
                ],
                status="planned",
                version=1
            )
            db.add(demo_brief)
            db.commit()

    return user
