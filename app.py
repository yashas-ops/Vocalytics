"""AI Interview Analyzer — Streamlit Application Entrypoint

Dark-themed SaaS-style dashboard (D-11 navy palette).
Single-file app with internal page routing (D-02).
Three pages: Upload, Dashboard, History.
"""

import streamlit as st
from pathlib import Path

from modules.audio_pipeline import extract_audio
from modules.transcription import transcribe_audio
from utils.file_manager import save_upload, get_file_size_mb, allowed_file
from database.init import insert_interview
from modules.speech_analysis import analyze_speech
from modules.visual_analysis import analyze_visual
from modules.scoring import compute_confidence, generate_feedback, calc_filler_rate
from database.init import update_interview
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

# Set dark theme for Plotly charts (per D-12)
pio.templates.default = "plotly_dark"

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Interview Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
def load_css():
    """Load custom dark navy theme CSS."""
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Page Routing ──
# Internal page navigation via sidebar radio (D-02: not st.navigation)
# Track current page in session state so it persists across reruns
if "page" not in st.session_state:
    st.session_state.page = "Upload"

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🎯 AI Interview Analyzer")
    st.markdown("---")
    st.markdown("### Navigation")

    if st.button("📤 Upload", use_container_width=True):
        st.session_state.page = "Upload"
        st.rerun()
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
        st.rerun()
    if st.button("📋 History", use_container_width=True):
        st.session_state.page = "History"
        st.rerun()

    st.markdown("---")
    st.markdown(
        "*Upload a mock interview video to receive "
        "AI-powered feedback on your communication skills.*",
        unsafe_allow_html=True,
    )
    if "last_interview_id" in st.session_state:
        st.markdown(f"**Latest:** Interview `{st.session_state.last_interview_id}`")
    st.markdown("---")
    st.caption("v0.1.0 — Fully Local AI")


# ── Page Content ──
def render_upload_page():
    """Upload page — accepts video files for analysis."""
    st.title("Upload Interview")
    st.markdown("Upload a mock interview video to analyze your performance.")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "mov", "avi"],
            help="Supported formats: MP4, MOV, AVI (max 500MB)",
        )

        if uploaded_file is not None:
            if not allowed_file(uploaded_file.name):
                ext = Path(uploaded_file.name).suffix
                st.error(f"Unsupported format: {ext}. Use mp4, mov, or avi.")
                return

            size_mb = uploaded_file.size / (1024 * 1024)
            st.success(f"📁 **{uploaded_file.name}** ({size_mb:.1f} MB) ready for analysis")

            if st.button("🚀 Analyze Interview", type="primary", use_container_width=True):
                progress_bar = st.progress(0, text="Starting pipeline...")
                with st.status("Processing interview...", expanded=True) as status:
                    try:
                        # Step 1: Save video
                        progress_bar.progress(10, text="Saving video...")
                        st.write("📁 Saving video to uploads/...")
                        video_path = save_upload(uploaded_file)
                        st.session_state.last_video_path = video_path
                        interview_id = insert_interview(video_path)
                        st.write(f"✅ Video saved ({get_file_size_mb(video_path):.1f} MB)")
                        st.write(f"📋 Interview ID: `{interview_id}`")

                        # Step 2: Extract audio
                        progress_bar.progress(30, text="Extracting audio...")
                        st.write("🎵 Extracting audio (16kHz mono WAV)...")
                        try:
                            audio_result = extract_audio(video_path)
                        except FileNotFoundError as e:
                            st.error(f"❌ {str(e)}")
                            status.update(label="Pipeline failed: ffmpeg missing", state="error")
                            return
                        if not audio_result.success:
                            st.error("❌ Audio extraction failed. Ensure ffmpeg is installed and on your PATH.")
                            status.update(label="Audio extraction failed", state="error")
                            return
                        st.write(f"✅ Audio extracted: {audio_result.duration_sec:.0f}s duration")
                        st.write(f"   Saved to: `{audio_result.audio_path}`")

                        # Step 3: Transcribe
                        progress_bar.progress(60, text="Transcribing (faster-whisper)...")
                        st.write("📝 Transcribing speech to text...")
                        st.caption("This may take a moment depending on video length. "
                                    f"Expected: ~{audio_result.duration_sec:.0f}s of audio.")
                        try:
                            transcript = transcribe_audio(audio_result.audio_path)
                        except Exception as e:
                            st.error(f"❌ Transcription error: {str(e)}")
                            status.update(label="Pipeline failed", state="error")
                            return
                        st.write(f"✅ Transcription complete: {len(transcript.segments)} segments")
                        st.write(f"   Model: `{transcript.model_used}`")
                        st.write(f"   Total duration: {transcript.duration_sec:.1f}s")

                        # Step 4: Analyze speech
                        progress_bar.progress(80, text="Analyzing speech patterns...")
                        st.write("🔤 Analyzing filler words and speaking speed...")
                        try:
                            speech_result = analyze_speech(transcript)
                        except Exception as e:
                            st.error(f"❌ Speech analysis error: {str(e)}")
                            status.update(label="Speech analysis failed", state="error")
                            return
                        st.write(f"✅ Speech analysis complete: {speech_result.total_filler_count} filler words, "
                                  f"{speech_result.wpm:.0f} WPM ({speech_result.speed_classification})")

                        # Store in session state
                        st.session_state.last_transcript = transcript
                        st.session_state.last_speech_analysis = speech_result
                        st.session_state.last_interview_id = interview_id

                        # Complete
                        progress_bar.progress(100, text="Pipeline complete!")
                        status.update(label="Analysis complete", state="complete", expanded=False)

                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                        status.update(label="Pipeline failed", state="error")
                        return

                # Display results after pipeline
                st.markdown("---")
                st.markdown("### 📝 Transcript")
                st.markdown(f"**{len(transcript.segments)} segments** across {transcript.duration_sec:.1f}s")

                for i, seg in enumerate(transcript.segments):
                    with st.expander(f"Segment {i+1}: {seg.start:.1f}s – {seg.end:.1f}s"):
                        st.write(seg.text)

                with st.expander("📄 Full Transcript Text", expanded=False):
                    st.text_area("Full transcript", transcript.full_text, height=200, disabled=True)

                # Display speech analysis results
                st.markdown("### 🗣️ Speech Analysis")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Speaking Speed",
                              f"{speech_result.wpm:.0f} WPM",
                              help=f"Classification: {speech_result.speed_classification}")
                with col_b:
                    st.metric("Filler Words",
                              str(speech_result.total_filler_count),
                              help=f"Across {speech_result.total_words} total words")
                with col_c:
                    top = speech_result.top_filler or "—"
                    st.metric("Most Used Filler", top)

                # Color coding for speed classification
                speed = speech_result.speed_classification
                if speed == "fast":
                    st.warning(f"⚡ Speaking speed is **{speed}** ({speech_result.wpm:.0f} WPM). "
                              f"Aim for 110–160 WPM for best clarity.")
                elif speed == "slow":
                    st.warning(f"🐢 Speaking speed is **{speed}** ({speech_result.wpm:.0f} WPM). "
                              f"Try to pace up to 110–160 WPM.")
                else:
                    st.success(f"✅ Speaking speed is **{speed}** ({speech_result.wpm:.0f} WPM). "
                              f"Great pacing!")

                if speech_result.filler_words:
                    st.markdown("**Filler Word Breakdown:**")
                    filler_data = {
                        fw.word: fw.count
                        for fw in sorted(
                            speech_result.filler_words,
                            key=lambda x: x.count,
                            reverse=True
                        )
                    }
                    st.dataframe(
                        {"Word": list(filler_data.keys()), "Count": list(filler_data.values())},
                        use_container_width=True,
                        hide_index=True,
                    )

                # ── Visual Analysis (Step 5) ──
                # Visual analysis is independent — it processes the video file directly,
                # not the transcript. Can run after speech analysis.
                st.markdown("---")
                st.markdown("### 👁️ Visual Analysis")

                try:
                    progress_bar.progress(85, text="Analyzing eye contact and emotions...")
                    st.write("🎯 Analyzing eye contact with MediaPipe Face Mesh...")

                    eye_result, emotion_result = analyze_visual(video_path)

                    # Store in session state
                    st.session_state.last_eye_contact = eye_result
                    st.session_state.last_emotion = emotion_result

                    # Display eye contact results
                    st.write(f"✅ Eye contact: {eye_result.contact_percentage:.0f}% "
                              f"({eye_result.contact_frames}/{eye_result.total_frames} frames)")

                    # Display emotion results
                    st.write(f"✅ Emotions analyzed across {emotion_result.frames_analyzed} frames")
                    st.write(f"   Dominant emotion: **{emotion_result.dominant_emotion}**")

                    # Show emotion distribution as a small bar chart
                    if emotion_result.emotion_distribution:
                        emotion_df = pd.DataFrame(
                            list(emotion_result.emotion_distribution.items()),
                            columns=["Emotion", "Frequency"]
                        )
                        st.dataframe(emotion_df, use_container_width=True, hide_index=True)

                except Exception as e:
                    # Visual analysis is non-critical — pipeline continues without it
                    st.warning(f"⚠️ Visual analysis encountered an issue: {str(e)}")
                    st.caption("Transcript and speech analysis are still available. "
                              "Visual results will show as unavailable on the Dashboard.")
                    # Set defaults so dashboard doesn't crash
                    st.session_state.last_eye_contact = None
                    st.session_state.last_emotion = None
                    # Provide defaults for scoring even when visual analysis fails
                    default_eye_result = None   # compute_confidence handles None-equivalent
                    default_emotion_result = None

                # ── Step 6: Confidence scoring, feedback, and persistence ──
                progress_bar.progress(95, text="Computing confidence score...")
                st.write("📊 Computing confidence score and generating feedback...")

                # Extract values from analysis results (handling None for failed visual analysis)
                eye_result = st.session_state.get("last_eye_contact")
                emotion_result = st.session_state.get("last_emotion")
                eye_contact_pct = eye_result.contact_percentage if eye_result is not None else 0.0
                dominant_emotion = emotion_result.dominant_emotion if emotion_result is not None else "uncertain"

                # Calculate filler rate
                filler_rate = calc_filler_rate(speech_result.total_filler_count, speech_result.total_words)

                # Compute confidence scores
                confidence = compute_confidence(
                    eye_contact_pct=eye_contact_pct,
                    filler_rate_per_100=filler_rate,
                    wpm=speech_result.wpm,
                    speed_classification=speech_result.speed_classification,
                    dominant_emotion=dominant_emotion,
                )

                # Generate feedback report
                feedback = generate_feedback(
                    confidence=confidence,
                    eye_contact_pct=eye_contact_pct,
                    filler_rate_per_100=filler_rate,
                    filler_count=speech_result.total_filler_count,
                    wpm=speech_result.wpm,
                    speed_classification=speech_result.speed_classification,
                    dominant_emotion=dominant_emotion,
                )

                # Store in session state for Dashboard display
                st.session_state.last_confidence = confidence
                st.session_state.last_feedback = feedback

                # Persist all results to SQLite
                st.write("💾 Saving results to database...")

                # Serialize complex data to JSON for DB storage
                transcript_json = json.dumps([
                    {"start": seg.start, "end": seg.end, "text": seg.text}
                    for seg in transcript.segments
                ]) if transcript else None

                filler_words_json = json.dumps([
                    {"word": fw.word, "count": fw.count}
                    for fw in speech_result.filler_words
                ]) if speech_result.filler_words else None

                emotion_distribution_json = json.dumps(
                    emotion_result.emotion_distribution
                ) if emotion_result and emotion_result.emotion_distribution else None

                # Build single UPDATE call with all fields (D-13: single write)
                update_interview(
                    interview_id=interview_id,
                    # Transcription
                    transcript_text=transcript.full_text if transcript else None,
                    transcript_json=transcript_json,
                    # Speech analysis
                    filler_words_json=filler_words_json,
                    total_filler_count=speech_result.total_filler_count,
                    top_filler=speech_result.top_filler,
                    wpm=speech_result.wpm,
                    speed_classification=speech_result.speed_classification,
                    total_words=speech_result.total_words,
                    # Visual analysis
                    eye_contact_percentage=eye_contact_pct,
                    eye_contact_frames=eye_result.contact_frames if eye_result else None,
                    dominant_emotion=dominant_emotion,
                    emotion_distribution_json=emotion_distribution_json,
                    # Confidence scores
                    confidence_eye_contact=confidence.eye_contact_score,
                    confidence_filler=confidence.filler_score,
                    confidence_pacing=confidence.pacing_score,
                    confidence_emotion=confidence.emotion_score,
                    confidence_clarity=confidence.clarity_score,
                    confidence_composite=confidence.composite,
                    confidence_classification=confidence.classification,
                    # Feedback
                    feedback_text=feedback,
                )

                st.write(f"✅ Confidence score: **{confidence.composite:.0f}/100** ({confidence.classification})")
                st.write(f"✅ Feedback report generated")

                progress_bar.progress(100, text="Pipeline complete!")
                status.update(label="Analysis complete", state="complete", expanded=False)

                st.success("✅ Analysis complete! Visit the **Dashboard** page to view detailed results.")
                st.rerun()

    with col2:
        st.markdown("### Supported Formats")
        st.markdown("- MP4")
        st.markdown("- MOV")
        st.markdown("- AVI")
        st.markdown("### Requirements")
        st.markdown("- Max file size: 500 MB")
        st.markdown("- Clear audio recommended")
        st.markdown("- Single speaker")


def render_dashboard_page():
    """Dashboard page — displays analysis results."""
    st.title("Dashboard")
    st.markdown("View your interview analysis results.")

    st.markdown("---")

    # Check if analysis data exists
    speech = st.session_state.get("last_speech_analysis")
    transcript = st.session_state.get("last_transcript")

    if speech is None:
        # Placeholder state — no analysis run yet
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Confidence Score", "—", help="Overall confidence score (0-100)")
        with col2:
            st.metric("Eye Contact", "—", help="Percentage of time looking at camera")
        with col3:
            st.metric("Speaking Speed", "—", help="Words per minute")
        with col4:
            st.metric("Filler Words", "—", help="Total filler word count")

        st.info("📊 Analysis results will appear here after running an interview. "
                "Return to the Upload page to submit a video.")
        st.markdown("### Transcript")
        st.text_area("Transcript", "", height=150,
                     placeholder="Transcribed text will appear here...",
                     disabled=True)
        st.markdown("### Analysis Report")
        st.info("💡 Feedback report will be generated after analysis.")
        return

    # ── Analysis results available ──

    # Top row: Video preview + Metric cards (per D-09)
    col_video, col_metrics = st.columns([2, 3])  # 40% video, 60% metrics

    with col_video:
        video_path = st.session_state.get("last_video_path")
        if video_path:
            st.video(video_path)
        else:
            st.info("Video preview not available")

    with col_metrics:
        # 2x2 grid of metric cards
        col_a, col_b = st.columns(2)
        col_c, col_d = st.columns(2)

        with col_a:
            confidence = st.session_state.get("last_confidence")
            if confidence is not None:
                score = confidence.composite
                cls = confidence.classification
                st.metric("Confidence Score", f"{score:.0f}/100",
                          help=f"Classification: {cls}")
            else:
                st.metric("Confidence Score", "—")

        with col_b:
            eye_contact = st.session_state.get("last_eye_contact")
            if eye_contact is not None:
                contact_pct = f"{eye_contact.contact_percentage:.0f}%"
                st.metric("Eye Contact", contact_pct,
                          help=f"Based on {eye_contact.total_frames} sampled frames")
            else:
                st.metric("Eye Contact", "—", help="Not available")

        with col_c:
            speech = st.session_state.get("last_speech_analysis")
            if speech is not None:
                wpm = f"{speech.wpm:.0f}"
                st.metric("Speaking Speed", f"{wpm} WPM",
                          help=f"Classification: {speech.speed_classification}")
            else:
                st.metric("Speaking Speed", "—")

        with col_d:
            if speech is not None:
                st.metric("Filler Words", str(speech.total_filler_count),
                          help=f"Out of {speech.total_words} total words")
            else:
                st.metric("Filler Words", "—")

    # Confidence color indicator (below metric cards)
    if confidence is not None:
        score = confidence.composite
        cls = confidence.classification
        if cls == "Excellent":
            st.success(f"✅ **{cls}** — Confidence score of **{score:.0f}/100**. Strong performance!")
        elif cls == "Good":
            st.warning(f"📊 **{cls}** — Confidence score of **{score:.0f}/100**. Solid foundation with room to grow.")
        else:
            st.error(f"📉 **{cls}** — Confidence score of **{score:.0f}/100**. Focus on the improvement areas below.")

    # Speed classification colored indicator
    speed = speech.speed_classification
    if speed == "fast":
        st.warning(f"⚡ Speaking speed: **{wpm} WPM ({speed})**. Aim for 110–160 WPM.")
    elif speed == "slow":
        st.warning(f"🐢 Speaking speed: **{wpm} WPM ({speed})**. Try to pace up to 110–160 WPM.")
    else:
        st.success(f"✅ Speaking speed: **{wpm} WPM ({speed})**. Great pacing!")

    # Transcript section
    st.markdown("---")
    st.markdown("### 📝 Transcript")
    if transcript:
        st.text_area("Full Transcript", transcript.full_text, height=200, disabled=True)
    else:
        st.info("Transcript not available.")

    # Filler word breakdown section
    st.markdown("### 🗣️ Filler Word Analysis")

    if speech.filler_words:
        col_a, col_b = st.columns([3, 2])
        with col_a:
            st.markdown(f"**Total filler words:** {speech.total_filler_count}")
            st.markdown(f"**Most used:** `{speech.top_filler or '—'}`")
            st.markdown(f"**Speaking duration:** {speech.duration_minutes:.1f} minutes")
            st.markdown(f"**Total words spoken:** {speech.total_words}")

        with col_b:
            # Prepare filler breakdown for display
            filler_data = {
                fw.word: fw.count
                for fw in sorted(
                    speech.filler_words,
                    key=lambda x: x.count,
                    reverse=True
                )
            }
            st.dataframe(
                {"Word": list(filler_data.keys()), "Count": list(filler_data.values())},
                use_container_width=True,
                hide_index=True,
            )

        # Filler rate per 100 words
        if speech.total_words > 0:
            rate = (speech.total_filler_count / speech.total_words) * 100
            st.caption(f"Filler rate: **{rate:.1f}** per 100 words "
                       f"(~1 every {speech.total_words // max(speech.total_filler_count, 1)} words)")
    else:
        st.success("🎯 No filler words detected! Clean speech.")

    # ── Visual Analysis Results ──
    st.markdown("---")
    st.markdown("### 👁️ Eye Contact & Emotion Analysis")

    eye_contact = st.session_state.get("last_eye_contact")
    emotion = st.session_state.get("last_emotion")

    if eye_contact is None and emotion is None:
        st.info("📹 Visual analysis results will appear here after running an interview "
                "with a visible face. Return to the Upload page to submit a video.")

    else:
        col_ec, col_em = st.columns(2)

        with col_ec:
            if eye_contact is not None and eye_contact.total_frames > 0:
                pct = eye_contact.contact_percentage
                st.metric("Eye Contact", f"{pct:.0f}%")

                # Text annotation per D-19
                if pct >= 70:
                    st.success(f"✅ Good — maintained eye contact {pct:.0f}% of the time")
                elif pct >= 40:
                    st.warning(f"👀 Moderate eye contact ({pct:.0f}%) — try to look at the camera more")
                else:
                    st.error(f"📉 Low eye contact ({pct:.0f}%) — practice looking at the camera")

                st.caption(f"Based on {eye_contact.total_frames} sampled frames "
                           f"({eye_contact.contact_frames} with eye contact)")
            else:
                st.metric("Eye Contact", "—")
                st.info("No face detected — ensure you're visible on camera")

        with col_em:
            if emotion is not None and emotion.frames_analyzed > 0:
                st.metric("Dominant Emotion", emotion.dominant_emotion.capitalize())

                # Emotion frequency distribution — Plotly horizontal bar chart (per D-11, D-12)
                if emotion.emotion_distribution:
                    st.markdown("**Emotion Distribution:**")
                    emotion_df = pd.DataFrame(
                        list(emotion.emotion_distribution.items()),
                        columns=["Emotion", "Frequency"]
                    )
                    # Sort by frequency descending for the bar chart
                    emotion_df = emotion_df.sort_values("Frequency", ascending=True)

                    fig_emotion = px.bar(
                        emotion_df,
                        x="Frequency",
                        y="Emotion",
                        orientation='h',
                        title=None,
                        text_auto='.0%',
                        color="Frequency",
                        color_continuous_scale="blues",
                        height=250,
                    )
                    fig_emotion.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_title=None,
                        yaxis_title=None,
                        showlegend=False,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig_emotion, use_container_width=True)
                    st.caption(f"Analyzed across {emotion.frames_analyzed} keyframes")
            else:
                st.metric("Dominant Emotion", "—")
                st.info("Emotion analysis not available")

    # ── Confidence Score Gauge ──
    if confidence is not None:
        st.markdown("---")
        st.markdown("### 📊 Confidence Score Breakdown")

        # Gauge chart for composite score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confidence.composite,
            title={'text': f"Overall — {confidence.classification}"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cccccc"},
                'bar': {'color': "#636efa", 'thickness': 0.3},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 60], 'color': '#5a1a1a'},     # Dark red
                    {'range': [60, 80], 'color': '#5a4a1a'},     # Dark yellow
                    {'range': [80, 100], 'color': '#1a4a1a'},    # Dark green
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': confidence.composite,
                },
            },
        ))
        fig_gauge.update_layout(
            height=250,
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#cccccc", 'size': 14},
        )

        # Component breakdown (5 side-by-side metrics)
        col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
        components = [
            ("Eye Contact", confidence.eye_contact_score),
            ("Filler Words", confidence.filler_score),
            ("Pacing", confidence.pacing_score),
            ("Clarity", confidence.clarity_score),
            ("Emotion", confidence.emotion_score),
        ]
        for col, (label, score) in zip([col_s1, col_s2, col_s3, col_s4, col_s5], components):
            col.metric(label, f"{score:.0f}")

        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Feedback Report ──
    st.markdown("---")
    st.markdown("### 📋 Feedback Report")

    feedback = st.session_state.get("last_feedback")
    if feedback:
        with st.expander("View Detailed Feedback Report", expanded=False):
            st.markdown(feedback)
    else:
        st.info("💡 Feedback report will be generated after running an analysis.")


def render_history_page():
    """History page — shows past interview sessions with click-to-view."""
    st.title("History")
    st.markdown("Browse your past interview sessions.")
    st.markdown("---")

    # Fetch all interviews from database
    from database.init import fetch_all_interviews
    interviews = fetch_all_interviews()

    if not interviews:
        st.info("📋 No interview sessions yet. Upload your first interview to get started.")
        st.markdown("### Recent Sessions")
        st.caption("No sessions yet. Upload your first interview to get started.")
        return

    # Summary table (per D-15)
    st.markdown(f"**{len(interviews)} session(s)**")

    # Build table data
    table_data = []
    for row in interviews:
        table_data.append({
            "Date": row.get("created_at", "")[:10] if row.get("created_at") else "—",
            "Score": f"{row.get('confidence_composite', 0):.0f}/100" if row.get("confidence_composite") else "—",
            "Class": row.get("confidence_classification", "—"),
            "WPM": f"{row.get('wpm', 0):.0f}" if row.get("wpm") else "—",
            "Fillers": str(row.get("total_filler_count", "—")),
            "Eye Contact": f"{row.get('eye_contact_percentage', 0):.0f}%" if row.get("eye_contact_percentage") else "—",
            "Emotion": row.get("dominant_emotion", "—").capitalize() if row.get("dominant_emotion") else "—",
            "ID": row.get("id", ""),
        })

    df = pd.DataFrame(table_data)

    # Display table without ID column
    display_cols = ["Date", "Score", "Class", "WPM", "Fillers", "Eye Contact", "Emotion"]
    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    # Click-to-view per D-16: select interview from dropdown
    st.markdown("### View Full Report")
    interview_options = {
        f"{row['Date']} — Score: {row['Score']} — {row['Emotion']}": row["ID"]
        for row in table_data
    }

    selected_label = st.selectbox(
        "Select an interview to view:",
        options=list(interview_options.keys()),
        index=None,
        placeholder="Choose an interview...",
    )

    if selected_label and st.button("📊 View Report", type="primary", use_container_width=True):
        selected_id = interview_options[selected_label]
        load_interview_to_session(selected_id)
        st.session_state.page = "Dashboard"
        st.rerun()


def load_interview_to_session(interview_id: str):
    """Load a past interview's data into session state and navigate to Dashboard.

    Fetches the full record from SQLite and reconstructs session state
    so the Dashboard can display it using its existing rendering logic.
    """
    from database.init import fetch_interview
    from modules.models import (
        ConfidenceScores, SpeechAnalysisResult, FillerWordCount,
        EyeContactResult, EmotionResult, TranscriptionResult, TranscriptionSegment,
    )
    import json

    row = fetch_interview(interview_id)
    if row is None:
        st.error("Interview not found.")
        return

    # Reconstruct ConfidenceScores
    confidence = ConfidenceScores(
        eye_contact_score=row.get("confidence_eye_contact", 0.0),
        filler_score=row.get("confidence_filler", 0.0),
        pacing_score=row.get("confidence_pacing", 0.0),
        emotion_score=row.get("confidence_emotion", 0.0),
        clarity_score=row.get("confidence_clarity", 0.0),
        composite=row.get("confidence_composite", 0.0),
        classification=row.get("confidence_classification", "Needs Improvement"),
    )

    # Reconstruct SpeechAnalysisResult
    filler_words_json = row.get("filler_words_json")
    filler_words = []
    if filler_words_json:
        try:
            fw_list = json.loads(filler_words_json)
            filler_words = [FillerWordCount(**fw) for fw in fw_list]
        except (json.JSONDecodeError, TypeError):
            pass

    total_filler_count = row.get("total_filler_count", 0) or 0
    wpm = row.get("wpm", 0.0) or 0.0
    total_words = row.get("total_words", 0) or 0
    speed_classification = row.get("speed_classification", "slow")
    duration_sec = row.get("duration_sec", 0.0) or 0.0

    speech_analysis = SpeechAnalysisResult(
        filler_words=filler_words,
        total_filler_count=total_filler_count,
        top_filler=row.get("top_filler"),
        wpm=wpm,
        speed_classification=speed_classification,
        total_words=total_words,
        duration_minutes=duration_sec / 60.0 if duration_sec else 0.0,
    )

    # Reconstruct EyeContactResult
    eye_contact_pct = row.get("eye_contact_percentage", 0.0) or 0.0
    eye_contact_frames = row.get("eye_contact_frames", 0) or 0
    eye_result = EyeContactResult(
        contact_percentage=eye_contact_pct,
        total_frames=eye_contact_frames,
        contact_frames=int(eye_contact_pct * eye_contact_frames / 100.0) if eye_contact_frames > 0 else 0,
        frame_results=[],
    )

    # Reconstruct EmotionResult
    emotion_json = row.get("emotion_distribution_json")
    emotion_distribution = {}
    if emotion_json:
        try:
            emotion_distribution = json.loads(emotion_json)
        except (json.JSONDecodeError, TypeError):
            pass

    emotion_result = EmotionResult(
        dominant_emotion=row.get("dominant_emotion", "uncertain") or "uncertain",
        emotion_distribution=emotion_distribution,
        frames_analyzed=len(emotion_distribution) if emotion_distribution else 0,
    )

    # Reconstruct TranscriptionResult
    transcript_text = row.get("transcript_text", "") or ""
    transcript_json_str = row.get("transcript_json")
    segments = []
    if transcript_json_str:
        try:
            seg_list = json.loads(transcript_json_str)
            segments = [TranscriptionSegment(**seg) for seg in seg_list]
        except (json.JSONDecodeError, TypeError):
            pass

    transcript = TranscriptionResult(
        segments=segments,
        full_text=transcript_text,
        model_used="history",
        duration_sec=duration_sec,
    )

    # Populate session state
    st.session_state.last_confidence = confidence
    st.session_state.last_feedback = row.get("feedback_text", "")
    st.session_state.last_speech_analysis = speech_analysis
    st.session_state.last_transcript = transcript
    st.session_state.last_eye_contact = eye_result
    st.session_state.last_emotion = emotion_result
    st.session_state.last_interview_id = interview_id
    st.session_state.last_video_path = row.get("video_path", "")


# Route to the correct page
page = st.session_state.page

if page == "Upload":
    render_upload_page()
elif page == "Dashboard":
    render_dashboard_page()
elif page == "History":
    render_history_page()
