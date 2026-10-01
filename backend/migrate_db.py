import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'copilot.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check creator_profiles
    cursor.execute("PRAGMA table_info(creator_profiles)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    new_profile_cols = [
        ("experience_level", "TEXT DEFAULT 'Beginner'"),
        ("preferred_duration", "TEXT DEFAULT '30-60 seconds'"),
        ("tone", "TEXT DEFAULT 'Simple, practical, energetic'"),
        ("topics_liked", "JSON DEFAULT '[]'"),
        ("topics_avoided", "JSON DEFAULT '[]'"),
        ("platforms", "JSON DEFAULT '[\"Instagram Reels\"]'"),
        ("posting_frequency", "TEXT DEFAULT '3-4 times a week'"),
    ]

    for col_name, col_def in new_profile_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE creator_profiles ADD COLUMN {col_name} {col_def}")
            print(f"Added column {col_name} to creator_profiles")

    # Check content_briefs
    cursor.execute("PRAGMA table_info(content_briefs)")
    brief_cols = {row[1] for row in cursor.fetchall()}

    new_brief_cols = [
        ("content_objective", "TEXT DEFAULT 'High engagement education'"),
        ("recommended_hook", "TEXT DEFAULT 'direct'"),
        ("hashtags", "JSON DEFAULT '[]'"),
        ("editing_notes", "JSON DEFAULT '[]'"),
        ("b_roll_requirements", "JSON DEFAULT '[]'"),
        ("audio_requirements", "JSON DEFAULT '[]'"),
        ("platform_notes", "JSON DEFAULT '[]'"),
        ("meta_info", "JSON DEFAULT '{}'"),
    ]

    for col_name, col_def in new_brief_cols:
        if col_name not in brief_cols:
            cursor.execute(f"ALTER TABLE content_briefs ADD COLUMN {col_name} {col_def}")
            print(f"Added column {col_name} to content_briefs")

    # Check content_ideas
    cursor.execute("PRAGMA table_info(content_ideas)")
    idea_cols = {row[1] for row in cursor.fetchall()}
    if "meta_info" not in idea_cols:
        cursor.execute("ALTER TABLE content_ideas ADD COLUMN meta_info JSON DEFAULT '{}'")
        print("Added column meta_info to content_ideas")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")
else:
    print(f"Database {db_path} does not exist.")
