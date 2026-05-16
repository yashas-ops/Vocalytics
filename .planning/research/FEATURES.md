# Feature Research

**Domain:** AI Interview Analysis / Communication Coaching
**Researched:** 2026-05-16
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Video upload & webcam recording | User needs to get their video into the system first | LOW | ffmpeg/moviepy handles this; webcam through Streamlit's `st.camera_input` |
| Speech-to-text transcription | Core analysis depends on what was said; every competitor (Yoodli, Huru, Interview Sidekick) provides this | MEDIUM | Whisper tiny/base on CPU — expect 5-15s per minute of audio |
| Filler word detection (um, uh, like, etc.) | **#1 most cited actionable metric** in user reviews of Yoodli and competitors | LOW | Regex/text pattern matching on transcript — trivial once transcription exists |
| Speaking speed / WPM analysis | Every tool from Yoodli to Genius Interview to LHH Interview Center tracks pacing and benchmarks it | LOW | Count words in transcript, divide by duration — simple math |
| Overall score / confidence rating | Yoodli gives 45% rubric score, Huru scores hundreds of data points, Genius Interview gives 91/100 — users expect a number | MEDIUM | Heuristic weighted formula (filler words, WPM, eye contact, emotion, clarity) |
| Transcript with timestamps | Foundation for any text analysis and keyword spotting | MEDIUM | Whisper returns segments with start/end timestamps naturally |
| Session history / dashboard | Users want to see progress over time — Yoodli's "trend tracking" is its highest-rated feature | MEDIUM | SQLite persistence + Streamlit session listing + trend charts |
| Feedback report (strengths, weaknesses, tips) | Table stakes output — every tool generates post-session feedback | MEDIUM | Template-based with spaCy NLP; ties together all metrics into narrative |

### Differentiators (Competitive Advantage)

Features that set the product apart from cloud-dependent competitors.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **100% local processing (privacy)** | No video leaves the laptop. Competitors Yoodli, Huru, Final Round AI all upload to cloud. This is the strongest differentiator for privacy-conscious users (and a portfolio showcase) | LOW | By design — no cloud code written. Built-in constraint, not an added feature |
| **No account/signup needed** | Zero friction. Competing tools (Yoodli: max 5 free sessions, then paywall; Huru: subscription) all require account creation | LOW | Streamlit single-user mode. No auth middleware needed |
| **Emotion / facial expression analysis** | Yoodli tracks eye contact but NOT emotions. Genius Interview analyzes body language but NOT emotions. DeepFace/FER adds a genuinely unique dimension — "you appeared nervous 60% of the time" | HIGH | DeepFace/FER on CPU via keyframe sampling (every 5-10s) — heavy but viable with keyframe approach |
| **Eye contact detection** | Yoodli does this via webcam; Genius Interview advertises it; MirrorAI emphasizes it. Still differentiating because many tools skip it or do it poorly | MEDIUM | MediaPipe Face Mesh — well-documented, works on CPU, reliable with face orientation |
| **Template-based feedback (no LLM)** | Competitors (Final Round AI, Skillora) rely on GPT/Claude APIs. Template-based spaCy approach is local-only, explainable, and infinitely reproducible | MEDIUM | spaCy for NLP patterns, jinja2/string templates for report generation |
| **CPU-only philosophy** | Runs on any laptop. Most competitors assume cloud GPU or powerful hardware. Being local-first but CPU-friendly is architectural differentiation | MEDIUM | Keyframe sampling, Whisper tiny/base, MediaPipe CPU mode — all deliberately chosen |
| **Heuristic confidence score** | Explainable scoring (not "AI magic"). Users can understand why they got a 72 vs an 85 — formula is transparent | LOW | Weighted formula documented in the UI itself creates trust |
| **Keyframe-based video processing** | Full-video emotion analysis at 30fps would be unusable on CPU. Keyframe sampling (1 frame per 5-10s) makes CPU-only emotion analysis viable | MEDIUM | Requires deciding sampling rate; risk of missing micro-expressions is acceptable for MVP |

### Anti-Features (What NOT to Build)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time AI answer copilot | Users want live prompting during interviews (Interview Sidekick, OphyAI, Beyz AI all offer this) | Requires cloud API, real-time audio processing, and screen-sharing stealth mode — completely out of scope for local-only tool | Post-session analysis + practice recording |
| LLM-generated answer suggestions | Users want AI to tell them what to say | Requires API calls (OpenAI, Claude), breaks local-only constraint, and the cost/power story doesn't work | Template-based feedback on how they answered, not what to say |
| Resume parsing / job matching | Adjacent functionality users ask for | Major scope expansion — would require NLP resume parsing, job board APIs, recommendation engine | Don't build. Focus on communication coaching, not job search |
| Multi-user authentication | "This would be great for my friends/team" | Adds auth, session management, data isolation — overkill for local single-user app | Single-user only. If demand materializes, reconsider later |
| Mobile app (iOS/Android) | Users want to practice anywhere | Entire tech stack is Streamlit/Python — not portable to mobile. Would need separate native app | Streamlit responsive web app works on phone browser |
| Docker / containerization | Dev-ops minded users ask for this | Adds container overhead, build complexity, no benefit for local single-user app | Simple `pip install` + `streamlit run` |
| Cloud backup / sync | Users want data accessible across devices | Requires cloud infrastructure, authentication, sync logic — contradicts local-only constraint | SQLite file can be manually backed up by user |
| Gamification / leaderboards | Genius Interview has 11 games and XP grinding | Consumer engagement pattern — not aligned with professional interview coaching. Distracts from core value | Driver: measurable improvement, not entertainment |
| Two-sided interview analysis (both participants) | Advanced users want full conversation dynamics | Doubles processing time, requires speaker diarization, much more complex UI | Focus on individual practice. Both-sides is v2+ territory |

## Feature Dependencies

```
Video Upload / Recording
    └──requires──> Audio Extraction (moviepy/ffmpeg)
                       └──requires──> Speech-to-Text (Whisper)
                                          ├──requires──> Filler Word Detection
                                          ├──requires──> WPM / Speed Analysis
                                          └──enhances──> Feedback Report (needs transcript)

Webcam Recording (separate path)
    └──requires──> Video Upload (same pipeline after capture)

Eye Contact Detection (MediaPipe)
    └──requires──> Video Frames (from same uploaded video)
    └──enhances──> Confidence Score

Emotion Analysis (DeepFace/FER)
    └──requires──> Keyframe Extraction
    └──requires──> Video Frames
    └──enhances──> Confidence Score

Confidence Score
    └──requires──> Filler Word Detection
    └──requires──> WPM / Speed Analysis
    └──requires──> Eye Contact Detection
    └──requires──> Emotion Analysis

Feedback Report
    └──requires──> Transcript (for content patterns)
    └──requires──> Filler Word Detection
    └──requires──> WPM / Speed Analysis
    └──requires──> Eye Contact Detection
    └──requires──> Emotion Analysis
    └──requires──> Confidence Score

Dashboard
    └──requires──> ALL analysis components (displays all results)
    └──requires──> SQLite persistence (session history)

Session History / Trends
    └──requires──> Dashboard
    └──requires──> SQLite persistence
```

### Dependency Notes

- **All video analysis is downstream of Video Upload:** There's a single ingestion point. Whether the user records via webcam or uploads a file, the same pipeline processes it. This simplifies the architecture.
- **Speech-to-text is the critical bottleneck:** Whisper on CPU is the slowest step (5-15x real-time). Everything textual depends on it. This phase determines overall processing time.
- **Eye contact and emotion run in parallel on the same video frames:** They read from the same extracted frames but use different models (MediaPipe vs DeepFace). No cross-dependency between them — they can process concurrently.
- **Confidence score is a reduction of all metrics:** It's a weighted formula that aggregates everything. Build it last, after all metrics are producing stable output.
- **Feedback report reads ALL metrics:** It's the final output. Nothing depends on it, it depends on everything.

## MVP Definition

### Launch With (v1) — Core Pipeline

The minimum feature set that delivers the core value proposition: *upload a video, get comprehensive feedback*.

- [x] **Video upload (mp4, mov, avi)** — entry point for analysis
- [x] **Webcam recording** — alternative entry point, lower friction
- [x] **Audio extraction** — necessary for speech-to-text
- [x] **Speech-to-text via Whisper tiny/base** — foundation of text analysis
- [x] **Filler word detection** — most actionable communication metric
- [x] **WPM / speaking speed analysis** — pacing is critical for interviews
- [x] **Eye contact detection (MediaPipe)** — non-verbal differentiator
- [x] **Emotion analysis (DeepFace/FER keyframes)** — unique differentiator
- [x] **Confidence score (heuristic weighted)** — overall performance number
- [x] **Template-based feedback report** — actionable output user can take away
- [x] **Dashboard with video preview + all metrics** — single-screen consumption
- [x] **SQLite session history** — enables progress tracking

### Add After Validation (v1.x)

Features to add once core pipeline is stable and working on real user laptops.

- [ ] **Trend charts (filler words over time, WPM over time)** — users who do multiple sessions want this. Yoodli users rate this as their #1 feature. Add once >=3 sessions exist in DB
- [ ] **Export report as PDF** — shareable artifact. Simple `pdfkit` or `reportlab` integration
- [ ] **Custom filler word list** — industry-specific filler words (e.g., "actually" in consulting, "literally" in tech). Requires UI for adding/removing words
- [ ] **Transcript search / keyword highlight** — "was I saying 'um' during my answer about leadership?" — text search is cheap once transcript exists
- [ ] **Video scrubber with metric sync** — "show me where I lost eye contact" — timeline visualization linking metrics to video position. High UX value
- [ ] **Comparison view (two sessions side-by-side)** — "my second attempt was better, show me" — requires all session data already stored

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **AI question generation (spaCy-based, not LLM)** — generate practice questions from transcript topic analysis. Template-based question bank is possible without APIs
- [ ] **Accent/diction analysis** — identify pronunciation patterns. Requires phoneme-level analysis. Complex, narrow value
- [ ] **Posture analysis (MediaPipe Pose)** — sitting posture during interview. Adds body language dimension. More models = slower processing
- [ ] **Speaker diarization for multi-participant** — would enable analyzing back-and-forth. Very complex, needs v2+ timeline
- [ ] **Audio tone / pitch analysis** — emotional tone of voice beyond words. Would add vocal confidence dimension. Research-stage complexity
- [ ] **Topic modeling of answers** — "you talk about 'teamwork' 40% of the time, 'results' 30%" — spaCy-based topic extraction, interesting but not essential

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Video upload + webcam recording | HIGH | LOW (Streamlit built-in) | P1 |
| Audio extraction | HIGH | LOW (moviepy one-liner) | P1 |
| Speech-to-text (Whisper) | HIGH | MEDIUM (model download + inference) | P1 |
| Filler word detection | HIGH | LOW (regex) | P1 |
| WPM / speed analysis | HIGH | LOW (word count / duration) | P1 |
| Eye contact detection | HIGH | MEDIUM (MediaPipe inference) | P1 |
| Emotion analysis | MEDIUM | HIGH (DeepFace keyframe inference) | P1 (differentiator) |
| Confidence score | HIGH | LOW (weighted formula) | P1 |
| Template feedback report | HIGH | MEDIUM (spaCy + templates) | P1 |
| Dashboard (single session) | HIGH | MEDIUM (Streamlit layout) | P1 |
| SQLite session storage | MEDIUM | LOW (SQLite + SQLAlchemy) | P1 |
| Session history list | MEDIUM | LOW (SQLite query + list UI) | P1 |
| Trend charts (multi-session) | MEDIUM | MEDIUM (requires session history) | P2 |
| PDF export | LOW | MEDIUM (pdfkit setup) | P2 |
| Custom filler words | MEDIUM | LOW (config UI + list param) | P2 |
| Transcript search | LOW | LOW (text search on transcript) | P2 |
| Video-metric sync scrubber | MEDIUM | HIGH (frame-level timestamp mapping) | P2 |
| Side-by-side comparison | LOW | MEDIUM (dual-session render) | P3 |
| Question generation | LOW | MEDIUM (topic extraction) | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Yoodli ($8-20/mo) | Huru (subscription) | Genius Interview (free) | MirrorAI (free) | Our Approach |
|---------|-------------------|---------------------|----------------------|-----------------|--------------|
| **Filler word tracking** | ✅ Detailed | ✅ Detailed | ✅ Yes | ✅ Yes | ✅ Regex-based (simpler, no LLM) |
| **WPM / pacing** | ✅ Benchmarked | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Word count / duration |
| **Eye contact** | ✅ Webcam-based | ❌ Not mentioned | ✅ Real-time | ✅ Yes | ✅ MediaPipe Face Mesh |
| **Emotion analysis** | ❌ Not provided | ❌ Not provided | ❌ Body language only | ❌ Not provided | ✅ **DeepFace/FER — unique** |
| **Confidence score** | ✅ Rubric-based (45%) | ✅ "Hundreds of data points" | ✅ 91/100 | ❌ Not provided | ✅ Heuristic weighted (transparent) |
| **Transcript** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Whisper STT |
| **Feedback report** | ✅ Detailed rubrics | ✅ Action items | ✅ Annotations | ✅ Basic tips | ✅ Template-based (spaCy) |
| **Session history** | ✅ Trending dashboard | ❌ Not emphasized | ✅ Yes | ❌ Not emphasized | ✅ SQLite + Streamlit dashboard |
| **LLM-powered coaching** | ✅ Yes (cloud GPT) | ✅ Yes | ✅ Yes (cloud AI) | ❌ Not provided | ❌ **No LLM — template-based** |
| **Privacy (local-only)** | ❌ Cloud upload | ❌ Cloud upload | ❌ Cloud upload | ✅ Claims privacy | ✅ **100% local — key differentiator** |
| **No account required** | ❌ Account + paywall | ❌ Account + subscription | ❌ Account required | ✅ Free + no account | ✅ **No account needed** |
| **Real-time nudges** | ✅ During meetings | ❌ Not provided | ✅ Real-time | ❌ Not provided | ❌ Post-session only (per spec) |
| **AI mock interviewer** | ✅ Roleplay builder | ✅ Custom questions | ✅ AI Interviewer | ❌ Not provided | ❌ Not building (scope) |
| **Mobile support** | ✅ Yes | ✅ Yes | ✅ Mobile app | ✅ Mobile app | ❌ Streamlit web only |
| **Accent training** | ❌ Not provided | ❌ Not provided | ✅ Accent trainer | ❌ Not provided | ❌ Not building (v2+) |
| **Gamification** | ❌ Not provided | ❌ Not provided | ✅ 11 games + XP | ❌ Not provided | ❌ Explicit anti-feature |
| **Price** | $8-20/month | Subscription | Free | Free | **Free (no cloud costs)** |

**Key competitive insight:** No major competitor does emotion/facial expression analysis combined with eye contact detection in a single local tool. Yoodli is closest but is cloud-dependent and lacks emotion analysis. Genius Interview is free but cloud-based. **The combination of "fully local + emotion analysis + eye contact + filler words + WPM" is unique in this space.**

## Sources

- **Yoodli features and pricing:** yoodli.ai product pages, techraisal.com review, geniusfirms.com analysis, aidemos.com review
- **Genius Interview features:** genius-interviews.com product page
- **MirrorAI features:** mirrorai.perspect.ai product page
- **Huru features:** references in interviewsidekick.com comparison articles and finalroundai.com
- **Interview Sidekick / Final Round AI / OphyAI:** comparison tables at interviewsidekick.com/blog/best-ai-interview-coach
- **Market landscape:** socialtalent.com interview intelligence platform analysis, peoplebox.ai AI interview tools guide
- **Confidence level on competitor features:** MEDIUM (based on web research and product pages, not hands-on testing)
- **Confidence level on table stakes assessment:** HIGH (consistent across 10+ sources)

---
*Feature research for: AI Interview Analyzer*
*Researched: 2026-05-16*
