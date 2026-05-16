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

    # Metric cards with real data
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Confidence Score", "—", help="Coming in Phase 5")
    with col2:
        st.metric("Eye Contact", "—", help="Coming in Phase 4")
    with col3:
        wpm = f"{speech.wpm:.0f}"
        st.metric("Speaking Speed", f"{wpm} WPM",
                  help=f"Classification: {speech.speed_classification}")
    with col4:
        st.metric("Filler Words", str(speech.total_filler_count),
                  help=f"Out of {speech.total_words} total words")

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

    # Placeholder for future phase results
    st.markdown("---")
    st.markdown("### Analysis Report")
    st.info("💡 Full feedback report with confidence scoring will be available in Phase 5.")


def render_history_page():
    """History page — shows past interview sessions."""
    st.title("History")
    st.markdown("Browse your past interview sessions.")

    st.markdown("---")

    st.info("📋 Past interview history will appear here after your first analysis. "
            "Results are stored locally in the database.")

    # Placeholder for future history table
    st.markdown("### Recent Sessions")
    st.caption("No sessions yet. Upload your first interview to get started.")


# Route to the correct page
page = st.session_state.page

if page == "Upload":
    render_upload_page()
elif page == "Dashboard":
    render_dashboard_page()
elif page == "History":
    render_history_page()
