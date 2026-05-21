"""FastAPI server — serves React frontend, handles video uploads & analysis pipeline."""

import os
import uuid
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from utils.file_manager import allowed_file, save_upload_bytes
from utils.file_manager import UPLOAD_DIR
from database.init import (
    insert_interview, update_interview, fetch_interview,
    fetch_all_interviews, fetch_interviews_by_user,
    create_user, fetch_user_by_username, fetch_user_by_id,
)
from modules.auth import hash_password, verify_password, register_user, authenticate_user
from modules.audio_pipeline import extract_audio
from modules.transcription import transcribe_audio
from modules.speech_analysis import analyze_speech
from modules.eye_contact_enhanced import analyze_visual
from modules.scoring import compute_confidence, generate_feedback, calc_filler_rate

app = FastAPI(title="ctracker API")

# CORS for dev (Vite on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve uploaded videos for playback ──────────────────────────────────
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# ── Job store for async pipeline ────────────────────────────────────────
jobs: Dict[str, Dict[str, Any]] = {}


def _create_job_record() -> str:
    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "result": None,
        "error": None,
    }
    return job_id


def _format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS, matching app.py transcript display format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def _parse_feedback_sections(feedback_text: str) -> tuple[list[str], list[str]]:
    """Extract key strengths and coaching priorities from generated feedback text.

    The feedback text follows the template format from generate_feedback():

        ## Strengths
        ✅ first strength
        ✅ second strength

        ---

        ## Improvement Tips
        - **Tip title**: description
        - **Next tip**: description

    Returns:
        Tuple of (key_strengths, coaching_priorities), each a list of cleaned strings.
    """
    key_strengths: list[str] = []
    coaching_priorities: list[str] = []

    if not feedback_text:
        return key_strengths, coaching_priorities

    current_section: str | None = None
    for line in feedback_text.split("\n"):
        line_stripped = line.strip()

        # Detect section headers
        if line_stripped.startswith("## Strengths"):
            current_section = "strengths"
            continue
        elif line_stripped.startswith("## Improvement Tips"):
            current_section = "tips"
            continue
        elif line_stripped.startswith("##"):
            current_section = None
            continue

        if current_section == "strengths":
            if line_stripped.startswith("✅ "):
                cleaned = line_stripped[2:].strip()
                # Remove markdown bold markers
                cleaned = cleaned.replace("**", "")
                if cleaned:
                    key_strengths.append(cleaned)
            elif line_stripped and not line_stripped.startswith("##") and not line_stripped.startswith("---"):
                # Capture non-empty lines that aren't headers or separators
                # (handles fallback messages like "Keep practicing...")
                cleaned = line_stripped.replace("**", "")
                if cleaned:
                    key_strengths.append(cleaned)

        elif current_section == "tips" and line_stripped.startswith("- "):
            cleaned = line_stripped[2:].strip()
            # Clean up markdown bold: "**Title**: desc" → "Title: desc"
            cleaned = cleaned.replace("**", "")
            if cleaned:
                coaching_priorities.append(cleaned)

    return key_strengths, coaching_priorities


async def _run_pipeline(job_id: str, video_path: str, candidate_name: str, role_name: str, user_id: int = 0) -> None:
    try:
        jobs[job_id]["status"] = "processing"

        # Create interview record upfront (matching app.py:322 behavior)
        interview_id = insert_interview(video_path, candidate_name, role_name, user_id if user_id else None)

        jobs[job_id]["progress"] = 10
        audio_result = extract_audio(video_path)
        if not audio_result.success:
            raise RuntimeError(f"Audio extraction failed for {video_path}")

        jobs[job_id]["progress"] = 30
        transcript = transcribe_audio(audio_result.audio_path)

        jobs[job_id]["progress"] = 50
        speech_result = analyze_speech(transcript)

        jobs[job_id]["progress"] = 70
        eye_result: Optional[Any] = None
        emotion_result: Optional[Any] = None
        try:
            eye_result, emotion_result = analyze_visual(video_path)
        except Exception:
            eye_result = None
            emotion_result = None

        jobs[job_id]["progress"] = 85
        filler_rate = calc_filler_rate(
            speech_result.total_filler_count,
            speech_result.total_words,
        )
        eye_contact_pct = eye_result.contact_percentage if eye_result is not None else 0.0
        dominant_emotion = (
            emotion_result.dominant_emotion if emotion_result is not None else "uncertain"
        )
        confidence = compute_confidence(
            eye_contact_pct=eye_contact_pct,
            filler_rate_per_100=filler_rate,
            wpm=speech_result.wpm,
            speed_classification=speech_result.speed_classification,
            dominant_emotion=dominant_emotion,
        )
        feedback = generate_feedback(
            confidence=confidence,
            eye_contact_pct=eye_contact_pct,
            filler_rate_per_100=filler_rate,
            filler_count=speech_result.total_filler_count,
            wpm=speech_result.wpm,
            speed_classification=speech_result.speed_classification,
            dominant_emotion=dominant_emotion,
        )

        key_strengths, coaching_priorities = _parse_feedback_sections(feedback)

        video_filename = Path(video_path).name
        video_url = f"/uploads/{video_filename}"

        # Format segments matching app.py:387-389
        transcript_json = json.dumps(
            [{"start": s.start, "end": s.end, "text": s.text} for s in transcript.segments]
        )
        filler_words_json = (
            json.dumps([{"word": fw.word, "count": fw.count} for fw in speech_result.filler_words])
            if speech_result.filler_words else None
        )
        emotion_distribution_json = (
            json.dumps(emotion_result.emotion_distribution)
            if emotion_result is not None
            else None
        )

        # React frontend report
        report = {
            "id": interview_id,
            "timestamp": int(time.time() * 1000),
            "candidateName": candidate_name,
            "roleName": role_name,
            "durationSeconds": transcript.duration_sec,
            "overallScore": confidence.composite,
            "status": "report",
            "metrics": {
                "confidence": confidence.composite,
                "pacing": speech_result.wpm,
                "fillerCount": speech_result.total_filler_count,
                "eyeContact": eye_contact_pct,
                "coherence": confidence.composite,
            },
            "behavioralSignals": {
                "pacingFeedback": f"{speech_result.wpm:.0f} WPM, {speech_result.speed_classification}",
                "fillerWordsFeedback": f"{speech_result.total_filler_count} filler words",
                "eyeContactFeedback": f"{eye_contact_pct:.0f}% eye contact",
                "expressionFeedback": f"{dominant_emotion}",
            },
            "executiveSummary": feedback,
            "keyStrengths": key_strengths,
            "coachingPriorities": coaching_priorities,
            "transcript": [
                {
                    "speaker": "Candidate",
                    "timestamp": _format_timestamp(seg.start),
                    "text": seg.text,
                    "sentiment": "neutral",
                }
                for seg in transcript.segments
            ],
            "videoFileUrl": video_url,
            "emotionDistribution": emotion_result.emotion_distribution
                if emotion_result is not None
                else None,
        }

        update_interview(
            interview_id=interview_id,
            candidate_name=candidate_name,
            role_name=role_name,
            duration_sec=transcript.duration_sec,
            transcript_text=transcript.full_text,
            transcript_json=transcript_json,
            filler_words_json=filler_words_json,
            total_filler_count=speech_result.total_filler_count,
            top_filler=speech_result.top_filler,
            wpm=speech_result.wpm,
            speed_classification=speech_result.speed_classification,
            total_words=speech_result.total_words,
            eye_contact_percentage=eye_contact_pct,
            eye_contact_frames=eye_result.contact_frames if eye_result is not None else None,
            dominant_emotion=dominant_emotion,
            emotion_distribution_json=emotion_distribution_json,
            confidence_eye_contact=confidence.eye_contact_score,
            confidence_filler=confidence.filler_score,
            confidence_pacing=confidence.pacing_score,
            confidence_emotion=confidence.emotion_score,
            confidence_clarity=confidence.clarity_score,
            confidence_composite=confidence.composite,
            confidence_classification=confidence.classification,
            feedback_text=feedback,
        )

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = report
    except FileNotFoundError as exc:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = f"File not found: {exc}"
        jobs[job_id]["progress"] = 100
    except Exception as exc:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(exc)
        jobs[job_id]["progress"] = 100


# ── Auth Endpoints ──────────────────────────────────────────────────────

@app.post("/api/register")
async def api_register(username: str = Form(...), password: str = Form(...)):
    success, message = register_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...)):
    user_id = authenticate_user(username, password)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    user = fetch_user_by_id(user_id)
    return {"user_id": user_id, "username": user["username"]}


@app.get("/api/me")
async def api_me(user_id: int = 0):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = fetch_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user["id"], "username": user["username"]}


# ── API Endpoints ───────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_video(
    video: UploadFile = File(...),
    candidateName: str = Form("Candidate"),
    roleName: str = Form("Role"),
    userId: int = Form(0),
):
    """Upload a video and start analysis pipeline."""
    if not allowed_file(video.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use mp4, mov, or avi.")

    content = await video.read()
    upload_path = save_upload_bytes(video.filename, content)

    job_id = _create_job_record()
    asyncio.create_task(_run_pipeline(job_id, upload_path, candidateName, roleName, userId))

    return JSONResponse(content={"jobId": job_id, "status": "pending"})


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Poll pipeline progress and get result when done."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    response: dict[str, Any] = {
        "status": job["status"],
        "progress": job["progress"],
    }
    if job["status"] == "completed":
        response["result"] = job["result"]
    if job["status"] == "failed":
        response["error"] = job["error"]
    return JSONResponse(content=response)


@app.get("/api/history")
async def get_history(user_id: int = 0):
    """Return interviews, optionally filtered by user."""
    interviews = fetch_interviews_by_user(user_id) if user_id else fetch_all_interviews()
    results = []
    for row in interviews:
        results.append({
            "id": row.get("id", ""),
            "timestamp": row.get("created_at", ""),
            "candidateName": row.get("candidate_name", "Candidate"),
            "roleName": row.get("role_name", "Role"),
            "durationSeconds": row.get("duration_sec", 0) or 0,
            "overallScore": row.get("confidence_composite", 0) or 0,
            "metrics": {
                "confidence": row.get("confidence_composite", 0) or 0,
                "pacing": row.get("wpm", 0) or 0,
                "fillerCount": row.get("total_filler_count", 0) or 0,
                "eyeContact": row.get("eye_contact_percentage", 0) or 0,
                "coherence": row.get("confidence_composite", 0) or 0,
            },
            "videoFileUrl": f"/uploads/{Path(row.get('video_path', '')).name}" if row.get("video_path") else None,
        })
    return JSONResponse(content=results)


@app.get("/api/interview/{interview_id}")
async def get_interview(interview_id: str):
    """Return a full interview report by ID."""
    row = fetch_interview(interview_id)
    if not row:
        raise HTTPException(status_code=404, detail="Interview not found")

    emotion_dist = {}
    if row.get("emotion_distribution_json"):
        try:
            emotion_dist = json.loads(row["emotion_distribution_json"])
        except (json.JSONDecodeError, TypeError):
            emotion_dist = {}

    segments = []
    if row.get("transcript_json"):
        try:
            segments = json.loads(row["transcript_json"])
        except (json.JSONDecodeError, TypeError):
            segments = []

    key_strengths, coaching_priorities = _parse_feedback_sections(
        row.get("feedback_text", "") or ""
    )

    report = {
        "id": row["id"],
        "timestamp": row.get("created_at", ""),
        "candidateName": row.get("candidate_name", "Candidate"),
        "roleName": row.get("role_name", "Role"),
        "durationSeconds": row.get("duration_sec", 0) or 0,
        "overallScore": row.get("confidence_composite", 0) or 0,
        "status": "report",
        "metrics": {
            "confidence": row.get("confidence_composite", 0) or 0,
            "pacing": row.get("wpm", 0) or 0,
            "fillerCount": row.get("total_filler_count", 0) or 0,
            "eyeContact": row.get("eye_contact_percentage", 0) or 0,
            "coherence": row.get("confidence_composite", 0) or 0,
        },
        "behavioralSignals": {
            "pacingFeedback": f"{row.get('wpm', 0):.0f} WPM, {row.get('speed_classification', 'moderate')}",
            "fillerWordsFeedback": f"{row.get('total_filler_count', 0)} filler words",
            "eyeContactFeedback": f"{row.get('eye_contact_percentage', 0):.0f}% eye contact",
            "expressionFeedback": f"{row.get('dominant_emotion', 'neutral')}",
        },
        "executiveSummary": row.get("feedback_text", "") or "",
        "keyStrengths": key_strengths,
        "coachingPriorities": coaching_priorities,
        "transcript": [
            {
                "speaker": "Candidate",
                "timestamp": _format_timestamp(s.get("start", 0)),
                "text": s.get("text", ""),
                "sentiment": "neutral",
            }
            for s in segments
        ],
        "videoFileUrl": f"/uploads/{Path(row.get('video_path', '')).name}" if row.get("video_path") else None,
        "emotionDistribution": emotion_dist,
    }
    return JSONResponse(content=report)


# ── Serve built React frontend (production) — MUST be last ─────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="frontend_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if not full_path:
            return FileResponse(str(FRONTEND_INDEX))
        candidate = FRONTEND_DIR / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(FRONTEND_INDEX))
else:
    @app.get("/")
    async def root():
        return {"message": "ctracker API running. Build frontend with: cd frontend && npm run build"}


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.server:app", host="0.0.0.0", port=port)
