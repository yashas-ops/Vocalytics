"""SQLite database initialization and connection management.

Initializes on import with WAL mode for concurrent reads during analysis.
Single `interviews` table stores all analysis results (per D-06).
All confidence score fields defined up front (per D-08).
"""

import os
import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional

# Database file path — created in project root
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(DB_DIR), "database", "app.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with WAL mode and row factory set.

    Per D-07: WAL mode enables concurrent reads during analysis writes.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create the interviews table if it does not exist.

    Single-table design (D-06) — all analysis results stored as columns.
    JSON fields for complex nested data (segments, filler words, emotions).
    Score fields defined now (D-08) so schema is stable through Phase 5.
    """
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            video_path TEXT NOT NULL,
            duration_sec REAL,

            -- Phase 2: Transcription
            transcript_text TEXT,
            transcript_json TEXT,

            -- Phase 3: Speech Analysis
            filler_words_json TEXT,
            total_filler_count INTEGER DEFAULT 0,
            top_filler TEXT,
            wpm REAL,
            speed_classification TEXT,
            total_words INTEGER,

            -- Phase 4: Visual Analysis
            eye_contact_percentage REAL,
            eye_contact_frames INTEGER,
            dominant_emotion TEXT,
            emotion_distribution_json TEXT,

            -- Phase 5: Confidence Scores (defined now per D-08)
            confidence_eye_contact REAL DEFAULT 0.0,
            confidence_filler REAL DEFAULT 0.0,
            confidence_pacing REAL DEFAULT 0.0,
            confidence_emotion REAL DEFAULT 0.0,
            confidence_clarity REAL DEFAULT 0.0,
            confidence_composite REAL DEFAULT 0.0,
            confidence_classification TEXT DEFAULT 'Needs Improvement',

            -- Phase 5: Feedback
            feedback_text TEXT,

            -- Pipeline status
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    conn.close()


def generate_id() -> str:
    """Generate a unique interview ID."""
    return str(uuid.uuid4())[:8]


def insert_interview(video_path: str) -> str:
    """Insert a new interview record and return its ID."""
    interview_id = generate_id()
    created_at = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO interviews (id, created_at, video_path, status) VALUES (?, ?, ?, 'pending')",
        (interview_id, created_at, video_path)
    )
    conn.commit()
    conn.close()
    return interview_id


def update_interview(interview_id: str, **updates) -> None:
    """Update an existing interview record with analysis results.

    Dynamically builds SET clause from keyword arguments matching column names.
    Automatically sets status to 'complete'.

    Args:
        interview_id: The interview ID to update.
        **updates: Column-value pairs matching the interviews schema.
    """
    if not updates:
        return
    conn = get_connection()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values())
    values.append(interview_id)
    conn.execute(
        f"UPDATE interviews SET {set_clause}, status = 'complete' WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


def fetch_interview(interview_id: str) -> Optional[dict]:
    """Fetch a single interview record by ID.

    Args:
        interview_id: The interview ID to fetch.

    Returns:
        Dict of column:value if found, None otherwise.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM interviews WHERE id = ?", (interview_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_all_interviews() -> list:
    """Fetch all interview records ordered by creation date descending (per D-17).

    Returns:
        List of dicts, one per interview. Empty list if none exist.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM interviews ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Auto-initialize on import
init_db()
