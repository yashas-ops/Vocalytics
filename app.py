"""AI Interview Analyzer - Streamlit application entrypoint."""

from __future__ import annotations

import json
import textwrap
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from database.init import fetch_all_interviews, fetch_interview, insert_interview, update_interview
from modules.audio_pipeline import extract_audio
from modules.models import (
    ConfidenceScores,
    EmotionResult,
    EyeContactResult,
    FillerWordCount,
    SpeechAnalysisResult,
    TranscriptionResult,
    TranscriptionSegment,
)
from modules.scoring import calc_filler_rate, compute_confidence, generate_feedback
from modules.speech_analysis import analyze_speech
from modules.transcription import transcribe_audio
from modules.ui_presenters import (
    build_history_label,
    get_component_breakdown,
    get_dashboard_highlights,
    get_eye_contact_summary,
    get_score_summary,
    get_speed_summary,
)
from modules.eye_contact_enhanced import analyze_visual
from utils.file_manager import allowed_file, get_file_size_mb, save_upload

pio.templates.default = "plotly_dark"

st.set_page_config(
    page_title="AI Interview Analyzer",
    page_icon=":material/analytics:",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = ("Upload", "Dashboard", "History")


def load_css(theme: str) -> None:
    """Load custom UI styling and theme tokens."""
    pio.templates.default = "plotly_white" if theme == "Light" else "plotly_dark"

    with open("assets/styles.css", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

    if theme == "Light":
        st.markdown(
            textwrap.dedent("""
            <style>
            .stApp {
                --background: #faf9f7;
                --foreground: #171a19;
                --card: #ffffff;
                --border: rgba(0, 0, 0, 0.08);
                --muted: #f2f0e8;
                --muted-foreground: #555e59;
                --primary: #3f6f64;
                --primary-foreground: #ffffff;
                --accent: #588075;
                --accent-foreground: #ffffff;
                
                --bg: var(--background);
                --bg-subtle: #f4f2ec;
                --sidebar-bg: #f2f0e8;
                --surface: var(--card);
                --surface-raised: #f8f7f2;
                --surface-muted: var(--muted);
                --surface-inset: #ece9e0;
                --text: var(--foreground);
                --text-muted: var(--muted-foreground);
                --text-soft: #7a8480;
                --text-card: var(--foreground);
                --text-card-muted: var(--muted-foreground);
                --accent-hover: #4a7d72;
                --accent-text: var(--primary-foreground);
                --accent-soft: rgba(63, 111, 100, 0.12);
                --success: #3f7a62;
                --warning: #9a7642;
                --danger: #8f4a42;
                --shadow: 0 16px 36px rgba(31, 34, 31, 0.08);
                --shadow-soft: 0 8px 18px rgba(31, 34, 31, 0.06);
                --border-strong: rgba(0, 0, 0, 0.12);
                --radius: 8px;
            }

            /* Streamlit internal component overrides */
            div[data-testid="stStatusWidget"] {
                background: #ffffff !important;
                border-color: rgba(0, 0, 0, 0.08) !important;
            }
            div[data-testid="stStatusWidget"] * {
                color: #171a19 !important;
            }
            .stAlert {
                background: #ffffff !important;
                border-color: rgba(0, 0, 0, 0.08) !important;
            }
            section[data-testid="stSidebar"] .stRadio label p {
                color: #171a19 !important;
            }
            section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
                color: #171a19 !important;
            }
            div[data-testid="stMetric"] {
                background: #ffffff !important;
            }
            .stTabs [data-baseweb="tab-list"] {
                background: #f2f0e8 !important;
            }
            .stTabs [data-baseweb="tab"] {
                color: #5b635e !important;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background: #f8f7f2 !important;
                color: #171a19 !important;
            }
            .stDataFrame thead tr th {
                background: #f2f0e8 !important;
                color: #5b635e !important;
            }
            .streamlit-expanderHeader {
                color: #171a19 !important;
            }
            textarea:disabled {
                color: #3f4742 !important;
                background: #f2f0e8 !important;
            }
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapseButton"] {
                background-color: #f2f0e8 !important;
                border-color: rgba(0, 0, 0, 0.12) !important;
                color: #171a19 !important;
            }
            </style>
            """),
            unsafe_allow_html=True,
        )



def initialize_session_state() -> None:
    """Ensure required session-state keys exist."""
    defaults = {
        "page": "Upload",
        "last_interview_id": None,
        "last_video_path": None,
        "last_transcript": None,
        "last_speech_analysis": None,
        "last_eye_contact": None,
        "last_emotion": None,
        "last_confidence": None,
        "last_feedback": None,
        "theme": "Dark",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_surface_stack: list[object] = []


def surface_start(extra_class: str = "") -> None:
    """Start a styled native Streamlit container.

    Streamlit elements cannot be safely wrapped by sending an opening HTML tag
    in one block and a closing tag in another. A native container keeps widgets
    grouped while a hidden complete HTML anchor lets CSS apply surface variants.
    """
    container = st.container(border=True)
    _surface_stack.append(container)
    container.__enter__()

    class_name = "surface-anchor"
    if extra_class:
        class_name = f"{class_name} {extra_class}"
    st.markdown(f'<span class="{escape(class_name, quote=True)}"></span>', unsafe_allow_html=True)


def surface_end() -> None:
    """Close the current styled native Streamlit container."""
    if not _surface_stack:
        return
    container = _surface_stack.pop()
    container.__exit__(None, None, None)


def render_page_header(eyebrow: str, title: str, description: str) -> None:
    """Render a consistent page header."""
    st.markdown(
        textwrap.dedent(f"""
        <div class="page-header">
            <p class="page-eyebrow">{escape(eyebrow)}</p>
            <h1>{escape(title)}</h1>
            <p class="page-description">{escape(description)}</p>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str) -> None:
    """Render a section header inside a surface."""
    st.markdown(
        textwrap.dedent(f"""
        <div class="section-header">
            <h3>{escape(title)}</h3>
            <p>{escape(description)}</p>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_signal_callout(summary: dict[str, str]) -> None:
    """Render a callout using the tone returned by presentation helpers."""
    tone = summary["tone"]
    body = f"**{summary['headline']}**  \n{summary['body']}"

    if tone == "success":
        st.success(body)
    elif tone == "warning":
        st.warning(body)
    elif tone == "error":
        st.error(body)
    else:
        st.info(body)


def render_insight_cards(highlights: list[dict[str, str]]) -> None:
    """Render the overview insight cards."""
    if not highlights:
        st.info("Insights will appear here after a completed interview analysis.")
        return

    cards_html: list[str] = ['<div class="insight-grid">']
    for item in highlights:
        cards_html.append(
            textwrap.dedent(f"""
            <div class="insight-card tone-{escape(item["tone"])}">
                <p class="insight-label">{escape(item["label"])}</p>
                <h4>{escape(item["title"])}</h4>
                <p>{escape(item["body"])}</p>
            </div>
            """)
        )
    cards_html.append("</div>")
    st.markdown("".join(cards_html), unsafe_allow_html=True)


def render_component_bars(confidence: ConfidenceScores) -> None:
    """Render calm component bars for the score breakdown."""
    rows = ['<div class="component-bars">']
    for item in get_component_breakdown(confidence):
        rows.append(
            textwrap.dedent(f"""
            <div class="component-row tone-{escape(item["tone"])}">
                <div class="component-row-header">
                    <span>{escape(item["label"])}</span>
                    <strong>{escape(item["score"])}</strong>
                </div>
                <div class="component-track">
                    <span style="width: {escape(item["width"])}"></span>
                </div>
            </div>
            """)
        )
    rows.append("</div>")
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_signal_strip(
    confidence: ConfidenceScores,
    speech: SpeechAnalysisResult,
    eye_contact: EyeContactResult | None,
) -> None:
    """Render compact supporting metrics below the coaching summary."""
    eye_value = f"{eye_contact.contact_percentage:.0f}%" if eye_contact is not None else "N/A"
    items = [
        ("Confidence", f"{confidence.composite:.0f}/100"),
        ("Eye contact", eye_value),
        ("Speaking speed", f"{speech.wpm:.0f} WPM"),
        ("Filler words", str(speech.total_filler_count)),
    ]

    html = ['<div class="evidence-grid" aria-label="Supporting interview metrics">']
    for label, value in items:
        html.append(
            textwrap.dedent(f"""
            <div>
                <span>{escape(label)}</span>
                <strong>{escape(value)}</strong>
            </div>
            """)
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render sidebar navigation and context."""
    with st.sidebar:
        st.markdown(
            textwrap.dedent("""
            <div class="brand-profile">
                <div class="brand-kicker">Local analysis workspace</div>
                <h2>Interview Intelligence</h2>
                <p class="brand-subtitle">Speech, presence, and confidence review for practice interviews.</p>
                <div class="brand-meta">
                    <span>Private by default</span>
                    <span>v0.1.0</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        theme = st.segmented_control(
            "Appearance",
            options=["Dark", "Light"],
            default=st.session_state.theme,
        )
        if theme and theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()

        selected_page = st.radio(
            "Navigation",
            PAGES,
            index=PAGES.index(st.session_state.page),
            label_visibility="collapsed",
        )
        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()

        latest_id = st.session_state.get("last_interview_id")
        if latest_id:
            confidence = st.session_state.get("last_confidence")
            score_label = f"{confidence.composite:.0f}/100" if confidence is not None else "Pending"
            st.markdown(
                textwrap.dedent(f"""
                <div class="sidebar-note">
                    <p class="sidebar-label">Latest session</p>
                    <h4>{escape(str(latest_id))}</h4>
                    <p>Most recent confidence score: {escape(score_label)}</p>
                </div>
                """),
                unsafe_allow_html=True,
            )

        st.markdown(
            textwrap.dedent("""
            <div class="sidebar-note sidebar-note-muted">
                <p class="sidebar-label">Current flow</p>
                <ul>
                    <li>Upload a local recording.</li>
                    <li>Review the interview dossier.</li>
                    <li>Reopen prior sessions from the archive.</li>
                </ul>
            </div>
            """),
            unsafe_allow_html=True,
        )

        st.caption("v0.1.0 - Local-first analysis")


def run_analysis_pipeline(uploaded_file) -> None:
    """Run the existing interview analysis pipeline and store results."""
    progress_bar = st.progress(0, text="Preparing interview analysis...")

    with st.status("Running analysis", expanded=True) as status:
        try:
            progress_bar.progress(10, text="Saving upload...")
            st.write("Saving the interview video for local processing.")
            video_path = save_upload(uploaded_file)
            interview_id = insert_interview(video_path)
            st.session_state.last_video_path = video_path
            st.session_state.last_interview_id = interview_id

            progress_bar.progress(25, text="Extracting audio...")
            st.write(f"Saved video ({get_file_size_mb(video_path):.1f} MB).")
            audio_result = extract_audio(video_path)
            if not audio_result.success:
                st.error("Audio extraction failed. Ensure ffmpeg is installed and available on PATH.")
                status.update(label="Analysis failed during audio extraction", state="error")
                return
            st.write(f"Audio extracted from {audio_result.duration_sec:.0f}s of footage.")

            progress_bar.progress(50, text="Transcribing speech...")
            transcript = transcribe_audio(audio_result.audio_path)
            st.write(
                f"Transcription complete with {len(transcript.segments)} segments using "
                f"{transcript.model_used}."
            )

            progress_bar.progress(68, text="Scoring speech patterns...")
            speech_result = analyze_speech(transcript)
            st.write(
                f"Speech analysis finished: {speech_result.total_filler_count} filler words, "
                f"{speech_result.wpm:.0f} WPM."
            )

            progress_bar.progress(82, text="Reading visual signals...")
            eye_result: EyeContactResult | None = None
            emotion_result: EmotionResult | None = None
            try:
                eye_result, emotion_result = analyze_visual(video_path)
                st.write(
                    f"Visual analysis complete: {eye_result.contact_percentage:.0f}% eye contact, "
                    f"{emotion_result.dominant_emotion} expression."
                )
            except Exception as exc:  # pragma: no cover - visual stack is environment-dependent
                st.warning(f"Visual analysis could not complete: {exc}")

            progress_bar.progress(92, text="Generating feedback...")
            eye_contact_pct = eye_result.contact_percentage if eye_result is not None else 0.0
            dominant_emotion = (
                emotion_result.dominant_emotion if emotion_result is not None else "uncertain"
            )
            filler_rate = calc_filler_rate(
                speech_result.total_filler_count,
                speech_result.total_words,
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

            transcript_json = json.dumps(
                [{"start": seg.start, "end": seg.end, "text": seg.text} for seg in transcript.segments]
            )
            filler_words_json = json.dumps(
                [{"word": fw.word, "count": fw.count} for fw in speech_result.filler_words]
            ) if speech_result.filler_words else None
            emotion_distribution_json = (
                json.dumps(emotion_result.emotion_distribution)
                if emotion_result is not None and emotion_result.emotion_distribution
                else None
            )

            update_interview(
                interview_id=interview_id,
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

            st.session_state.last_transcript = transcript
            st.session_state.last_speech_analysis = speech_result
            st.session_state.last_eye_contact = eye_result
            st.session_state.last_emotion = emotion_result
            st.session_state.last_confidence = confidence
            st.session_state.last_feedback = feedback

            progress_bar.progress(100, text="Analysis complete.")
            status.update(label="Analysis complete", state="complete", expanded=False)

        except FileNotFoundError as exc:
            st.error(str(exc))
            status.update(label="Analysis failed", state="error")
            return
        except Exception as exc:  # pragma: no cover - depends on runtime models
            st.error(f"Unexpected analysis error: {exc}")
            status.update(label="Analysis failed", state="error")
            return

    st.session_state.page = "Dashboard"
    st.rerun()


def render_upload_page() -> None:
    """Render the upload page."""
    render_page_header(
        "Capture a session",
        "Upload a practice interview",
        "Run the local analysis pipeline and move directly into a structured review.",
    )

    main_col, side_col = st.columns([1.7, 1], gap="large")

    with main_col:
        surface_start("surface-hero")
        render_section_header(
            "Start a new analysis",
            "Supported formats: MP4, MOV, AVI. Clear audio and a visible face will produce the strongest feedback.",
        )
        st.markdown(
            textwrap.dedent("""
            <div class="process-meta" aria-label="Analysis stages">
                <span><strong>01</strong> Upload</span>
                <span><strong>02</strong> Transcribe</span>
                <span><strong>03</strong> Interpret</span>
                <span><strong>04</strong> Report</span>
            </div>
            """),
            unsafe_allow_html=True,
        )

        surface_start("upload-zone-anchor")
        uploaded_file = st.file_uploader(
            "Interview video",
            type=["mp4", "mov", "avi"],
            help="Maximum recommended size: 500 MB",
        )
        surface_end()

        if uploaded_file is not None:
            file_suffix = Path(uploaded_file.name).suffix.lower()
            size_mb = uploaded_file.size / (1024 * 1024)
            st.markdown(
                textwrap.dedent(f"""
                <div class="file-evidence">
                    <div>
                        <p class="file-label">File</p>
                        <h4>{escape(uploaded_file.name)}</h4>
                    </div>
                    <div>
                        <p class="file-label">Format</p>
                        <h4>{escape(file_suffix.replace('.', '').upper())}</h4>
                    </div>
                    <div>
                        <p class="file-label">Size</p>
                        <h4>{size_mb:.1f} MB</h4>
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )

            if not allowed_file(uploaded_file.name):
                st.error(f"Unsupported format: {file_suffix}. Use mp4, mov, or avi.")
            elif st.button("Analyze interview", type="primary", width="stretch"):
                run_analysis_pipeline(uploaded_file)

        surface_end()

    with side_col:
        surface_start()
        render_section_header(
            "Report coverage",
            "The review keeps interpretation first and leaves raw measurements available for deeper inspection.",
        )
        st.markdown(
            textwrap.dedent("""
            <div class="section-list">
                <div><strong>Executive summary</strong><span>Overall confidence classification and coaching priorities.</span></div>
                <div><strong>Behavioral signals</strong><span>Pacing, filler control, eye contact, and expression context.</span></div>
                <div><strong>Supporting record</strong><span>Transcript, saved history, and raw metric details.</span></div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        surface_end()

        latest_confidence = st.session_state.get("last_confidence")
        latest_id = st.session_state.get("last_interview_id")
        if latest_confidence is not None and latest_id is not None:
            surface_start("surface-muted")
            render_section_header(
                "Most recent result",
                "Jump back into the latest completed analysis at any time.",
            )
            st.metric("Confidence score", f"{latest_confidence.composite:.0f}/100")
            if st.button("Open latest dashboard", width="stretch"):
                st.session_state.page = "Dashboard"
                st.rerun()
            surface_end()


def render_dashboard_empty_state() -> None:
    """Render the dashboard state before any analysis has been run."""
    surface_start("surface-hero")
    render_section_header(
        "No interview analyzed yet",
        "Upload a recording to unlock the scorecard, transcript, and practice history.",
    )
    st.info("Your next completed interview will appear here automatically.")
    if st.button("Go to upload", type="primary", width="stretch"):
        st.session_state.page = "Upload"
        st.rerun()
    surface_end()


def render_dashboard_page() -> None:
    """Render the dashboard page."""
    render_page_header(
        "Review the session",
        "Dashboard",
        "A calm readout of confidence, coaching priorities, and supporting evidence.",
    )

    speech: SpeechAnalysisResult | None = st.session_state.get("last_speech_analysis")
    transcript: TranscriptionResult | None = st.session_state.get("last_transcript")
    confidence: ConfidenceScores | None = st.session_state.get("last_confidence")
    eye_contact: EyeContactResult | None = st.session_state.get("last_eye_contact")
    emotion: EmotionResult | None = st.session_state.get("last_emotion")

    if speech is None or confidence is None:
        render_dashboard_empty_state()
        return

    score_summary = get_score_summary(confidence.composite, confidence.classification)
    speed_summary = get_speed_summary(speech.speed_classification, speech.wpm)
    eye_summary = get_eye_contact_summary(
        eye_contact.contact_percentage if eye_contact is not None else None
    )
    highlights = get_dashboard_highlights(confidence, speech, eye_contact, emotion)

    hero_col, video_col = st.columns([1.4, 1], gap="large")

    with hero_col:
        surface_start("surface-hero executive-summary")
        render_section_header(
            "Executive summary",
            f"Session {st.session_state.last_interview_id or 'current'} - Composite score {confidence.composite:.0f}/100",
        )
        st.markdown(
            textwrap.dedent(f"""
            <div class="score-editorial tone-{escape(score_summary["tone"])}">
                <div>
                    <p class="score-label">Overall confidence</p>
                    <h2>{confidence.composite:.0f}</h2>
                </div>
                <div>
                    <p class="score-classification">{escape(confidence.classification)}</p>
                    <p>{escape(score_summary["body"])}</p>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        render_section_header(
            "Key coaching takeaways",
            "The highest-signal observations are kept short so the next practice session has a clear focus.",
        )
        render_insight_cards(highlights)
        surface_end()

    with video_col:
        surface_start()
        render_section_header(
            "Session recording",
            "Replay the source recording alongside the interpretation.",
        )
        video_path = st.session_state.get("last_video_path")
        if video_path:
            st.video(video_path)
        else:
            st.info("Video preview is not available for this session.")
        surface_end()

    render_signal_strip(confidence, speech, eye_contact)

    tabs = st.tabs(["Interpretation", "Transcript & Feedback", "Evidence"])

    with tabs[0]:
        overview_left, overview_right = st.columns([1.1, 1], gap="large")

        with overview_left:
            surface_start()
            render_section_header(
                "Behavioral interpretation",
                "These readings translate the measured signals into coaching language.",
            )
            render_signal_callout(speed_summary)
            render_signal_callout(eye_summary)
            surface_end()

            surface_start()
            render_section_header(
                "Confidence composition",
                "A restrained component view of the five weighted signals behind the score.",
            )
            render_component_bars(confidence)
            surface_end()

        with overview_right:
            surface_start()
            render_section_header(
                "Supporting metrics",
                "Compact measurements for pacing, verbal economy, and answer length.",
            )
            filler_rate = calc_filler_rate(speech.total_filler_count, speech.total_words)
            detail_cols = st.columns(2)
            detail_cols[0].metric("Total words", str(speech.total_words))
            detail_cols[1].metric("Filler rate", f"{filler_rate:.1f}/100")
            st.markdown(
                textwrap.dedent(f"""
                <div class="detail-list">
                    <div><span>Top filler</span><strong>{escape(speech.top_filler or 'None')}</strong></div>
                    <div><span>Duration</span><strong>{speech.duration_minutes:.1f} min</strong></div>
                    <div><span>Speed class</span><strong>{escape(speech.speed_classification.capitalize())}</strong></div>
                </div>
                """),
                unsafe_allow_html=True,
            )
            surface_end()

            surface_start()
            render_section_header(
                "Presence evidence",
                "Eye contact and expression are shown when the recording contains a readable face.",
            )
            if eye_contact is not None:
                st.metric("Eye contact", f"{eye_contact.contact_percentage:.0f}%")
                st.caption(
                    f"Based on {eye_contact.total_frames} sampled frames, "
                    f"{eye_contact.contact_frames} showed camera-facing eye contact."
                )
            else:
                st.info("Eye-contact data is unavailable for this session.")

            if emotion is not None and emotion.emotion_distribution:
                emotion_df = pd.DataFrame(
                    list(emotion.emotion_distribution.items()),
                    columns=["Emotion", "Frequency"],
                ).sort_values("Frequency", ascending=True)
                is_light = st.session_state.theme == "Light"
                color_scale = (
                    ["#e6e1d8", "#b9b1a4", "#716b61"] if is_light
                    else ["#252525", "#5d5a52", "#d8d1c3"]
                )
                font_c = "#191817" if is_light else "#f3f1ea"
                tick_c = "#6f6a60" if is_light else "#9a968d"
                fig_emotion = px.bar(
                    emotion_df,
                    x="Frequency",
                    y="Emotion",
                    orientation="h",
                    color="Frequency",
                    color_continuous_scale=color_scale,
                    height=260,
                    text_auto=".0%",
                )
                fig_emotion.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title=None,
                    yaxis_title=None,
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=font_c),
                )
                fig_emotion.update_xaxes(tickfont=dict(color=tick_c))
                fig_emotion.update_yaxes(tickfont=dict(color=tick_c))
                fig_emotion.update_traces(textfont=dict(color=font_c))
                st.plotly_chart(fig_emotion, width="stretch")
            else:
                st.info("Emotion distribution is unavailable for this session.")
            surface_end()

    with tabs[1]:
        transcript_col, feedback_col = st.columns([1.1, 0.9], gap="large")

        with transcript_col:
            surface_start()
            render_section_header(
                "Transcript",
                "Use the full transcript for content review and the timestamped segments for quick spot checks.",
            )
            if transcript is not None:
                st.text_area(
                    "Full transcript",
                    transcript.full_text,
                    height=320,
                    disabled=True,
                    label_visibility="collapsed",
                )
                if transcript.segments:
                    with st.expander("Show timestamped segments"):
                        for index, segment in enumerate(transcript.segments, start=1):
                            st.markdown(
                                f"**Segment {index} - {segment.start:.1f}s to {segment.end:.1f}s**"
                            )
                            st.write(segment.text)
            else:
                st.info("Transcript data is unavailable for this session.")
            surface_end()

        with feedback_col:
            surface_start()
            render_section_header(
                "Feedback report",
                "A deterministic summary generated from the same metrics shown elsewhere on the page.",
            )
            feedback = st.session_state.get("last_feedback")
            if feedback:
                st.markdown(feedback)
            else:
                st.info("Feedback will appear after a completed analysis.")
            surface_end()

    with tabs[2]:
        detail_left, detail_right = st.columns([1, 1], gap="large")

        with detail_left:
            surface_start()
            render_section_header(
                "Filler breakdown",
                "This table shows where verbal crutches are accumulating.",
            )
            if speech.filler_words:
                filler_data = {
                    filler.word: filler.count
                    for filler in sorted(speech.filler_words, key=lambda item: item.count, reverse=True)
                }
                st.dataframe(
                    {"Word": list(filler_data.keys()), "Count": list(filler_data.values())},
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.success("No filler words were detected in this session.")
            surface_end()

        with detail_right:
            surface_start()
            render_section_header(
                "Session metadata",
                "A quick read on what the current stored record contains.",
            )
            dominant_emotion = emotion.dominant_emotion.capitalize() if emotion is not None else "Unavailable"
            st.markdown(
                textwrap.dedent(f"""
                <div class="detail-list">
                    <div><span>Interview ID</span><strong>{escape(str(st.session_state.last_interview_id or 'Current'))}</strong></div>
                    <div><span>Confidence class</span><strong>{escape(confidence.classification)}</strong></div>
                    <div><span>Dominant emotion</span><strong>{escape(dominant_emotion)}</strong></div>
                    <div><span>Transcript model</span><strong>{escape(transcript.model_used if transcript else 'Unavailable')}</strong></div>
                </div>
                """),
                unsafe_allow_html=True,
            )
            surface_end()


def render_history_page() -> None:
    """Render the session history page."""
    render_page_header(
        "Track progress",
        "History",
        "Reopen saved sessions and compare progress without leaving the current workflow.",
    )

    interviews = fetch_all_interviews()
    if not interviews:
        surface_start("surface-hero")
        render_section_header(
            "No saved sessions yet",
            "Your completed analyses will appear here automatically once you run the first interview.",
        )
        if st.button("Upload your first interview", type="primary", width="stretch"):
            st.session_state.page = "Upload"
            st.rerun()
        surface_end()
        return

    table_data: list[dict[str, str]] = []
    numeric_scores: list[float] = []
    for row in interviews:
        score_value = row.get("confidence_composite")
        if score_value is not None:
            numeric_scores.append(float(score_value))

        table_data.append(
            {
                "Date": row.get("created_at", "")[:10] if row.get("created_at") else "N/A",
                "Score": f"{row.get('confidence_composite', 0):.0f}/100"
                if row.get("confidence_composite") is not None
                else "N/A",
                "Class": row.get("confidence_classification", "N/A"),
                "WPM": f"{row.get('wpm', 0):.0f}" if row.get("wpm") is not None else "N/A",
                "Fillers": str(row.get("total_filler_count", "N/A")),
                "Eye Contact": f"{row.get('eye_contact_percentage', 0):.0f}%"
                if row.get("eye_contact_percentage") is not None
                else "N/A",
                "Emotion": (
                    row.get("dominant_emotion", "N/A").capitalize()
                    if row.get("dominant_emotion")
                    else "N/A"
                ),
                "ID": row.get("id", ""),
            }
        )

    df = pd.DataFrame(table_data)
    st.markdown('<span class="archive-summary"></span>', unsafe_allow_html=True)
    summary_cols = st.columns(4)
    average_score = sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.0
    best_score = max(numeric_scores) if numeric_scores else 0.0

    summary_cols[0].metric("Saved sessions", str(len(table_data)))
    summary_cols[1].metric("Average score", f"{average_score:.0f}/100" if numeric_scores else "N/A")
    summary_cols[2].metric("Best score", f"{best_score:.0f}/100" if numeric_scores else "N/A")
    summary_cols[3].metric("Most recent", table_data[0]["Date"])

    table_col, resume_col = st.columns([1.4, 1], gap="large")

    with table_col:
        surface_start()
        render_section_header(
            "Session archive",
            "Use the table for scanning and the selector to reopen any saved report.",
        )
        st.dataframe(
            df[["Date", "Score", "Class", "WPM", "Fillers", "Eye Contact", "Emotion"]],
            width="stretch",
            hide_index=True,
        )
        surface_end()

    with resume_col:
        surface_start()
        render_section_header(
            "Resume a saved report",
            "Select a session and reopen it in the Dashboard view.",
        )
        interview_options = {build_history_label(row): row["ID"] for row in table_data}
        selected_label = st.selectbox(
            "Saved sessions",
            options=list(interview_options.keys()),
            label_visibility="collapsed",
        )

        selected_record = next(
            row for row in table_data if row["ID"] == interview_options[selected_label]
        )
        st.markdown(
            textwrap.dedent(f"""
            <div class="detail-list">
                <div><span>Date</span><strong>{escape(selected_record['Date'])}</strong></div>
                <div><span>Score</span><strong>{escape(selected_record['Score'])}</strong></div>
                <div><span>Class</span><strong>{escape(selected_record['Class'])}</strong></div>
                <div><span>Emotion</span><strong>{escape(selected_record['Emotion'])}</strong></div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        if st.button("Open selected report", type="primary", width="stretch"):
            load_interview_to_session(interview_options[selected_label])
            st.session_state.page = "Dashboard"
            st.rerun()
        surface_end()


def load_interview_to_session(interview_id: str) -> None:
    """Load a historical interview record into session state."""
    row = fetch_interview(interview_id)
    if row is None:
        st.error("Interview not found.")
        return

    confidence = ConfidenceScores(
        eye_contact_score=row.get("confidence_eye_contact", 0.0),
        filler_score=row.get("confidence_filler", 0.0),
        pacing_score=row.get("confidence_pacing", 0.0),
        emotion_score=row.get("confidence_emotion", 0.0),
        clarity_score=row.get("confidence_clarity", 0.0),
        composite=row.get("confidence_composite", 0.0),
        classification=row.get("confidence_classification", "Needs Improvement"),
    )

    filler_words_json = row.get("filler_words_json")
    filler_words: list[FillerWordCount] = []
    if filler_words_json:
        try:
            filler_words = [FillerWordCount(**item) for item in json.loads(filler_words_json)]
        except (json.JSONDecodeError, TypeError):
            filler_words = []

    total_filler_count = row.get("total_filler_count", 0) or 0
    duration_sec = row.get("duration_sec", 0.0) or 0.0
    speech_analysis = SpeechAnalysisResult(
        filler_words=filler_words,
        total_filler_count=total_filler_count,
        top_filler=row.get("top_filler"),
        wpm=row.get("wpm", 0.0) or 0.0,
        speed_classification=row.get("speed_classification", "slow"),
        total_words=row.get("total_words", 0) or 0,
        duration_minutes=duration_sec / 60.0 if duration_sec else 0.0,
    )

    eye_contact_pct = row.get("eye_contact_percentage")
    eye_result = None
    if eye_contact_pct is not None:
        eye_contact_frames = row.get("eye_contact_frames", 0) or 0
        eye_result = EyeContactResult(
            contact_percentage=eye_contact_pct,
            total_frames=eye_contact_frames,
            contact_frames=int(eye_contact_pct * eye_contact_frames / 100.0)
            if eye_contact_frames > 0
            else 0,
            frame_results=[],
        )

    emotion_distribution: dict[str, float] = {}
    emotion_json = row.get("emotion_distribution_json")
    if emotion_json:
        try:
            emotion_distribution = json.loads(emotion_json)
        except (json.JSONDecodeError, TypeError):
            emotion_distribution = {}

    emotion_result = None
    if row.get("dominant_emotion") or emotion_distribution:
        emotion_result = EmotionResult(
            dominant_emotion=row.get("dominant_emotion", "uncertain") or "uncertain",
            emotion_distribution=emotion_distribution,
            frames_analyzed=len(emotion_distribution) if emotion_distribution else 0,
        )

    segments: list[TranscriptionSegment] = []
    transcript_json_str = row.get("transcript_json")
    if transcript_json_str:
        try:
            segments = [TranscriptionSegment(**item) for item in json.loads(transcript_json_str)]
        except (json.JSONDecodeError, TypeError):
            segments = []

    transcript = TranscriptionResult(
        segments=segments,
        full_text=row.get("transcript_text", "") or "",
        model_used="history",
        duration_sec=duration_sec,
    )

    st.session_state.last_confidence = confidence
    st.session_state.last_feedback = row.get("feedback_text", "")
    st.session_state.last_speech_analysis = speech_analysis
    st.session_state.last_transcript = transcript
    st.session_state.last_eye_contact = eye_result
    st.session_state.last_emotion = emotion_result
    st.session_state.last_interview_id = interview_id
    st.session_state.last_video_path = row.get("video_path", "")


initialize_session_state()
load_css(st.session_state.theme)
render_sidebar()

page = st.session_state.page

if page == "Upload":
    render_upload_page()
elif page == "Dashboard":
    render_dashboard_page()
elif page == "History":
    render_history_page()
