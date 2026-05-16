# Pitfalls Research

**Domain:** Local AI Interview Analyzer (video-based: Whisper + MediaPipe + DeepFace + Streamlit)
**Researched:** 2026-05-16
**Confidence:** HIGH (pitfalls confirmed across multiple sources, official docs, and GitHub issues)

## Critical Pitfalls

### Pitfall 1: Whisper Hallucinates on Silence — Transcript Fills with Gibberish

**What goes wrong:**
During interview pauses, thinking breaks, or transitions (where there are 1-5 seconds of silence), Whisper doesn't output empty text — it *hallucinates*. The model fills silences with repeated phrases like "Thank you for watching" repeated 50+ times, or loops the last few words endlessly. This destroys WPM calculations, filler word counts, and transcript quality entirely.

**Why it happens:**
Whisper is a sequence-to-sequence model trained on speech data. When it encounters near-zero audio embeddings (silence), it "fills in" what it thinks should be there. It has no built-in Voice Activity Detection (VAD) — it transcribes every segment regardless of confidence. The `no_speech_prob` attribute exists in the output but is almost never checked. (Source: OpenAI Whisper community issues, whisper.cpp issue #1724, multiple confirmed reports.)

**How to avoid:**
- **Always pre-process audio with VAD** before passing to Whisper — strip silence segments. Use `webrtcvad`, `silero-vad`, or `pyannote.audio` to detect and remove non-speech regions.
- **Check `no_speech_prob` on each segment** and discard segments where probability of no-speech > 0.5 (or tune this threshold).
- **Use `faster-whisper`** (CTranslate2 backend) instead of `openai/whisper` — it provides `no_speech_prob` natively and is 4x faster on CPU.
- Set `temperature=0` and `compression_ratio_threshold=2.4` to reduce creative generation.

**Warning signs:**
- Filler word counts over 30% of total words (hallucinations often repeat filler-like patterns)
- Transcript contains repetitive loops ("thank you thank you thank you...")
- WPM > 250 even on a slow speaker (garbage words inflate count)
- Audio has detectable silence gaps but transcript has no gaps

**Phase to address:**
Phase 1 (Audio/Whisper pipeline) — VAD preprocessing must be built in from day one. Retrofitting it later means re-transcribing everything.

---

### Pitfall 2: Using `openai/whisper` Instead of `faster-whisper` on CPU — 4x Slowdown

**What goes wrong:**
Installing `openai-whisper` via pip and running `whisper.transcribe()` on CPU takes 3-5x longer than necessary. With `whisper-tiny` (the smallest model), a 10-minute interview takes ~8-12 minutes to transcribe on CPU with PyTorch. Users wait forever. The HuggingFace pipeline is even slower (~5x slower than PyTorch directly).

**Why it happens:**
The standard `openai/whisper` uses PyTorch for inference, which isn't optimized for CPU. `faster-whisper` uses CTranslate2 — a dedicated inference engine for Transformer models that is optimized for CPU with INT8 quantization. Benchmarks show PyTorch on 4-core CPU takes ~8s vs CTranslate2 being 4x faster with identical accuracy. (Source: SYSTRAN/faster-whisper GitHub, Modal blog benchmarks, PyPI docs.)

**How to avoid:**
- **Use `faster-whisper` from day one** — it's a drop-in replacement with identical output format.
- Enable INT8 quantization: `WhisperModel(model_size_or_path="tiny", device="cpu", compute_type="int8")`.
- If you must use `openai/whisper`, bypass the HuggingFace pipeline — call the raw model directly with `model.transcribe()` (not HF pipeline, which adds overhead).
- Consider ONNX Runtime or OpenVINO as alternative CPU optimizations.

**Warning signs:**
- Transcription takes longer than the audio duration
- CPU at 100% for the entire duration
- You installed `openai-whisper` without also evaluating `faster-whisper`

**Phase to address:**
Phase 1 (Audio/Whisper pipeline) — Model selection. Changing the ASR backend after building the pipeline around it is disruptive.

---

### Pitfall 3: Streaming Video Frame-by-Frame Through MediaPipe + DeepFace Destroys CPU Performance

**What goes wrong:**
Naively looping through every frame of a 10-minute interview video (18,000 frames at 30fps) and running MediaPipe Face Mesh + DeepFace emotion analysis on each frame. DeepFace alone takes 1-5 seconds per frame on CPU. Total time: 5-25 *hours* for one interview. App appears frozen, user assumes it's broken.

**Why it happens:**
DeepFace loads multiple deep learning models (detector + emotion classifier), and even with the lightweight `opencv` detector backend, each `DeepFace.analyze()` call loads and runs a full CNN. On CPU, this is inherently slow. MediaPipe is fast (~10-30ms per frame on CPU) but DeepFace is the bottleneck. Combined with frame-by-frame processing, this is a recipe for unusable performance. (Source: DeepFace GitHub issues #937, Stack Overflow reports of 3.6s per detection on CPU.)

**How to avoid:**
- **Process keyframes only, not every frame.** Extract 1 frame per second (or even 1 per 2-3 seconds) for emotion analysis. For a 10-min interview, that's 600 frames instead of 18,000.
- **Use OpenCV's face detector (Haar cascade) as a pre-filter** before DeepFace — skip frames where no face is detected at all.
- **Pre-warm the models** by running one "dummy" analysis at app startup (DeepFace loads models on first call, not import).
- **Use MediaPipe's face detection as the detector backend** for DeepFace (`detector_backend="mediapipe"`) — it's faster than OpenCV's default.
- Cache results: if frame N and frame N+5 have the same detected emotion, no need to re-analyze every intermediate frame.

**Warning signs:**
- Processing time grows linearly with framerate (should be sub-linear if sampling)
- CPU pinned at 100% for more than a few minutes
- No progress bar or estimated time remaining shown to user

**Phase to address:**
Phase 2 (Video Analysis — MediaPipe + DeepFace) — Frame sampling strategy is an architectural decision, not an optimization.

---

### Pitfall 4: Streamlit Loads Entire Video Into Memory — Crashes on Large Files

**What goes wrong:**
A user uploads a 500MB MP4 interview video via `st.file_uploader`. Streamlit stores the entire file in memory as a `BytesIO` object. Combined with the video being decoded by OpenCV (another copy), frames stored for processing (another copy), audio extracted (another copy), the app exceeds available RAM (especially on a typical 8GB laptop). The Streamlit server gets killed by the OS OOM killer. (Source: Streamlit GitHub issues #9218, #9460; Streamlit Discuss threads documenting 3.5GB+ upload crashes.)

**Why it happens:**
`st.file_uploader` keeps the entire file in server memory. OpenCV's `VideoCapture` also holds decoded frames in buffers. MoviePy writes temp audio files but Python keeps references. With video + audio + analysis results all in memory simultaneously, 1GB of video can balloon to 3-4GB of working set.

**How to avoid:**
- **Save uploaded video to disk immediately** — don't keep it in memory. Write `uploaded_file.getvalue()` to a temp file on disk, then work with file paths.
- **Use `tempfile.NamedTemporaryFile`** (with `delete=False`) for the video and clean up explicitly.
- **Set Streamlit's `server.maxUploadSize`** appropriately and _also_ validate file size client-side with a warning for files >200MB.
- **Process in stages, releasing memory between stages:** extract audio (saves audio file) → delete video reference → transcribe → release audio → analyze frames (process N frames at a time, not all at once).
- **Use `gc.collect()` explicitly** after large processing steps — Python's garbage collector may not reclaim memory fast enough in a tight loop.
- **Consider `streamlit-chunked-upload`** for very large files (>500MB).

**Warning signs:**
- RAM usage spikes when file upload completes
- Streamlit server exits with code 137 (OOM kill)
- Error: "Cannot allocate memory" or browser tab crashes
- App slows to a crawl after file upload

**Phase to address:**
Phase 1 (upload + file handling) — File storage strategy must be designed before any processing pipeline.

---

### Pitfall 5: Streamlit Reruns Your Entire ML Pipeline on Every UI Interaction

**What goes wrong:**
User uploads a video, processing begins, then they click a checkbox or adjust a slider in the dashboard. Streamlit reruns the entire script from top to bottom — including re-transcribing, re-analyzing every frame, and re-computing everything. The user waits 10+ minutes for the initial analysis, then a single click forces them to wait again.

**Why it happens:**
Streamlit's execution model reruns the full script on _every_ widget interaction. Without explicit caching, every import, model load, and computation runs again. ML models (Whisper, DeepFace, spaCy) are re-loaded into memory, then re-execute on the same data. (Source: Streamlit docs on execution model, Streamlit Discuss FAQ #64007.)

**How to avoid:**
- **Use `@st.cache_resource` for ML models** — Whisper model, DeepFace model, spaCy pipeline. These are non-serializable objects that should be loaded once and shared across all reruns.
- **Use `@st.cache_data` for analysis results** — the transcript, emotion data, eye contact scores. These are serializable and should persist until the input video changes.
- **Use `st.session_state` to track processing status** — "has this video been processed yet?" flags prevent re-processing.
- **Structure app as: upload → process button → session state flag → cache results → display.** The processing step should only run once per uploaded file, triggered by a button press (wrapped in `st.form` to batch the trigger).
- **Use `@st.fragment` (Streamlit >=1.33)** to make only the result-display sections rerun independently.

**Warning signs:**
- Console shows model loading logs on every UI interaction
- Processing spinner appears when changing a display setting
- UI is sluggish/unresponsive after initial analysis completes

**Phase to address:**
Phase 4 (Dashboard/UI integration) — But the caching architecture must be designed in Phase 0/1. Retrofitting caching after the pipeline is built means restructuring the entire app.

---

### Pitfall 6: Eye Contact Detection Fails Systematically — Gives 0% or Wrong Results

**What goes wrong:**
The eye contact metric shows 0% for a user who was clearly looking at the camera the entire time. Or it shows 100% for a user looking at their notes. The system loses all credibility for the core metric (eye contact).

**Why it happens:**
"Eye contact" is a deceptively hard problem. Common incorrect implementations:
1. **Using EAR (Eye Aspect Ratio)** alone — this measures eye openness (blinks), not gaze direction. A person can have eyes fully open but looking at notes, not camera.
2. **Confusing "face detected" with "looking at camera"** — MediaPipe detects the face even when looking 30 degrees away.
3. **Not accounting for head pose** — the correct approach requires head pose estimation (pitch/yaw/roll) using Perspective-n-Point (PnP) with known 3D facial landmarks.
4. **Using wrong landmark indices** — MediaPipe has 468-478 landmarks; using old 468-index code with the newer model returns wrong points. The `mp.solutions.face_mesh.FACEMESH_CONTOURS` provides correct sets.

Proper eye contact detection requires: (a) head pose estimation via solvePnP, (b) iris tracking (MediaPipe Iris model), (c) calibrated thresholds for looking-at-camera vs looking-away. (Source: MediaPipe Face Mesh docs, OpenCV PnP tutorial, academic papers on gaze estimation, Sander de Snaijer's landmark reference.)

**How to avoid:**
- **Implement head pose estimation using MediaPipe landmarks + OpenCV's `solvePnP`** — use known 3D face model points (nose tip, chin, left/right eye corners, mouth corners) and their 2D projections to compute yaw/pitch/roll angles.
- **Define "eye contact" as: head yaw within ±15°, pitch within ±10°, and irises centered** (MediaPipe Iris can provide iris landmarks).
- **Treat it as a heuristic, not ground truth** — document in the app that this is an approximation.
- **Test with multiple people** — the thresholds need calibration. What works for one face shape may not work for another.
- **Do NOT use "facing forward" as synonymous with "eye contact"** — they are different signals.

**Warning signs:**
- Eye contact score is binary (0% or 100%) — should be continuous
- Score correlates perfectly with "face detected" — means you're not measuring gaze
- Users report clearly inaccurate results during testing

**Phase to address:**
Phase 2 (Video Analysis — MediaPipe) — Building the wrong metric (e.g., EAR-only) means throwing away the landmark processing code and rewriting from scratch.

---

### Pitfall 7: Confidence Score Is an Opaque Black Box — User Can't Trust It

**What goes wrong:**
The system reports "Confidence Score: 74/100" with no explanation of what that means. The user has no idea whether 74 is good or bad, what contributes to it, or why another person scored 45. The metric feels like a magic number and undermines the entire feedback system.

**Why it happens:**
The natural instinct is to build a weighted formula: `0.3*wpm + 0.2*filler + 0.25*eye_contact + 0.25*emotion`. But without careful calibration, these weights are arbitrary. A person with great eye contact but a few filler words might get the same score as someone with poor eye contact but no fillers — and neither knows why.

**How to avoid:**
- **Make the score component-visible** — show a breakdown: "Eye Contact: 16/25, Filler Words: 8/25, Speaking Pace: 12/25, Confidence: 9/25 → Total: 45/100".
- **Calibrate weights against real interview data** — not just intuition. Record 10 mock interviews, score them manually, then tune weights to match human judgment.
- **Use percentile-based scoring, not absolute** — show "your eye contact was in the 70th percentile of all candidates" rather than raw scores.
- **Clearly label each metric's limitations** — "Eye contact is estimated from head pose (not true gaze tracking), results are approximate."
- **Include confidence intervals** — "Emotion analysis confidence: 68%" alongside the detected emotion.

**Warning signs:**
- Users ask "what does this score mean?"
- Two very different interview styles get identical scores
- No way to explain the score breakdown to a user
- Weights were chosen because they "felt right"

**Phase to address:**
Phase 3 (Feedback generation — heuristic scoring) — Building the scoring system without transparency means rebuilding it when users don't trust it.

---

### Pitfall 8: Emotion Detection on Keyframes Misses Emotional Transitions — Gives Stable-but-Wrong Results

**What goes wrong:**
You sample 1 frame per second for DeepFace emotion analysis, and the dashboard shows "Emotion: Neutral (78% of interview)". Meanwhile, the subject was clearly stressed/nervous at the start, relaxed in the middle, and confident at the end. The emotion analysis shows "neutral" throughout because keyframes happened to catch transitional expressions or the model's default is "neutral" for ambiguous expressions.

**Why it happens:**
DeepFace's emotion model (based on FER2013 or similar) is trained on static, posed expressions. It's biased toward "neutral" for non-posed faces. When you sample at 1fps, you catch micro-expressions, closed-eye frames (blinks), and transitional expressions that all get classified as "neutral." Additionally, DeepFace returns the _dominant_ emotion with a confidence score — but if no emotion exceeds 40% confidence, it still picks one, giving false precision. (Source: DeepFace docs on emotion models, MDPI emotion detection paper, IEEE study on real-time emotion detection limitations.)

**How to avoid:**
- **Use a confidence threshold** — only report an emotion if DeepFace confidence > 50%. Otherwise mark as "uncertain."
- **Aggregate emotions across frames using soft voting** — sum the confidence scores for each emotion across all frames, don't just take the per-frame dominant emotion.
- **Include the confidence in the UI** — "Anger detected (32% confidence)" is honest; "Anger detected" without context is misleading.
- **Sample at 1-2 fps but analyze in short windows** — aggregate over 5-10 second windows to smooth out noise.
- **Consider replacing DeepFace emotion with a simpler approach** — use MediaPipe's blendshape scores (52 blendshapes available in the Face Landmarker model) which include expression coefficients and run much faster on CPU since they reuse already-computed landmarks.

**Warning signs:**
- 80%+ of frames show "neutral" for visibly expressive speakers
- Emotion chart is essentially flat with rare spikes
- No "uncertain" or "low confidence" label appears anywhere
- Emotion changes every single frame (too noisy)

**Phase to address:**
Phase 2 (Video Analysis — DeepFace) and Phase 3 (Feedback generation)

---

### Pitfall 9: Temp Files Accumulate from MoviePy + FFmpeg — Disk Fills Up

**What goes wrong:**
Every video upload creates: (1) the uploaded video copy stored in Streamlit's temp, (2) an extracted audio WAV file from MoviePy, (3) any intermediate video clips, (4) temp files from Streamlit's media manager. Over a few uploads, this consumes 5-10GB of disk space on `C:`. Eventually operations start failing with "disk full" errors.

**Why it happens:**
MoviePy writes temp audio files during extraction but doesn't always clean them up (especially if the Python process is interrupted). Streamlit's media file manager keeps uploaded files in memory until the script finishes — but `@st.cache_data` can keep references alive indefinitely. On Windows, temp files in `%TEMP%` can be locked by the running process and not deletable until exit. (Source: MoviePy GitHub issues #1940, Streamlit Discuss #75511 on memory accumulation.)

**How to avoid:**
- **Always use `try/finally` blocks** to explicitly delete temp files after processing.
- **Use a dedicated temp directory** (e.g., `temp/` alongside the app) and clean it on app startup and shutdown.
- **Track file handles** — `cap.release()` for OpenCV, `VideoFileClip.close()` for MoviePy, then delete.
- **Set `st.cache_data`'s `ttl` and `max_entries`** to prevent indefinite caching of large files.
- **On app startup, clean `tempfile.gettempdir()`** of any files older than 1 hour.
- **Log file sizes** as files are created/deleted so disk issues are traceable.

**Warning signs:**
- `OSError: [Errno 28] No space left on device`
- Temp directory has hundreds of MB of `.wav` / `.mp4` files
- App works first time, fails on second upload
- Streamlit errors about "media file not found" (stale references)

**Phase to address:**
Phase 1 (upload + file handling) — Temp file hygiene isn't an optimization; it's a correctness requirement.

---

### Pitfall 10: Sequential Processing Pipeline = One Hour Wait for a 10-Minute Video

**What goes wrong:**
Processing flow: extract audio (30s) → transcribe with Whisper tiny (5 min) → analyze 600 keyframes with MediaPipe (5 min) → analyze 100 keyframe faces with DeepFace (10 min) → compute NLP stats (10s) → generate report (5s). Total: ~20 minutes. User uploads a video, gets no feedback for 20 minutes, assumes the app is broken, closes the tab.

**Why it happens:**
The pipeline is built as: `audio = extract(video)`, then `transcript = whisper(audio)`, then `landmarks = mediapipe(video)`, then `emotions = deepface(landmark_frames)`, then `report = generate(transcript, landmarks, emotions)`. Each step blocks on the previous. CPU cores sit idle while waiting for sequential I/O or single-threaded model inference.

**How to avoid:**
- **Parallelize where possible.** MediaPipe face analysis can run concurrently with Whisper transcription — they don't depend on each other.
- **Use `concurrent.futures.ThreadPoolExecutor`** to run audio extraction + video frame sampling simultaneously.
- **Use `asyncio` + `st.progress()`** to give the user real-time feedback on what's happening ("Transcribing audio... 45% complete").
- **Stream results to the UI incrementally** — show the transcript as it becomes available (Whisper segment by segment), then update emotion charts as analysis completes.
- **Pre-compute what you can** — load spaCy model and DeepFace models in parallel during app startup (using `@st.cache_resource`).
- **Set realistic expectations** — show estimated processing time before starting: "Processing typically takes 15-20 minutes for a 10-minute video."

**Warning signs:**
- App shows a single spinner for >30 seconds without any status update
- Task Manager shows some CPU cores at 0% while others are pegged
- Console shows sequential log messages with long gaps
- User asks "is it still working?"

**Phase to address:**
Phase 1-3 (pipeline design) — Parallelism and progress feedback must be designed into the pipeline architecture, not bolted on later.

---

### Pitfall 11: Wrong MediaPipe API Version — Code Written for Legacy API Breaks

**What goes wrong:**
You follow a tutorial from 2022 using `mp.solutions.face_mesh.FaceMesh()` and `mp.solutions.drawing_utils`. The code works locally. But when deploying or updating MediaPipe, it breaks because MediaPipe redesigned its API in May 2023 (moving from "solutions" to "tasks" API). The legacy API still works but is deprecated and has subtle bugs with newer model versions (468 vs 478 landmarks).

**Why it happens:**
Google significantly rearchitected MediaPipe in 2023. The old `mp.solutions.face_mesh` API is now "MediaPipe Legacy Solutions." The new API uses `FaceLandmarker` from `mediapipe.tasks.vision`. The new model outputs 478 landmarks (not 468), and the landmark indices shifted. Code using hardcoded old indices (e.g., 33 for left eye corner) returns wrong points with the new model. (Source: MediaPipe official docs redirect notice, GitHub issue discussions, Samuel Pröll's 2023 update post.)

**How to avoid:**
- **Pin MediaPipe version** — use `mediapipe==0.10.9` or whichever version you develop with. Document this in requirements.txt.
- **Decide up front: legacy API or new tasks API.** The legacy API (`mp.solutions`) is simpler for beginners but deprecated. The new API (`FaceLandmarker`) is the future but more verbose.
- **Use landmark index constants, not magic numbers** — define `LEFT_EYE_OUTER = 33` etc. as named constants so they can be updated if the model changes.
- **Test with at least 3 different face angles** when you update MediaPipe versions — check that landmark indices still map correctly.
- **Prefer `mediapipe` over `mediapipe-solutions`** — the latter is an older package.

**Warning signs:**
- Eye landmark indices return eyebrow coordinates instead
- Face detection works but landmarks look distorted/wrong
- Error about "module not found" for `mp.solutions`
- Drawing landmarks shows points in wrong locations

**Phase to address:**
Phase 0 (Setup / dependency management) — Choosing the wrong API version means rewriting all MediaPipe code in Phase 2.

---

### Pitfall 12: Filler Word Detection via Simple `in` Check Is Wrong

**What goes wrong:**
You implement filler word detection as: `for word in transcript.split(): if word.lower() in ["um", "uh", "like", "basically"]: count += 1`. This counts "umbrella" (contains "um"), "likeable" (contains "like"), "basically" used correctly as an actual word (not a filler). Reported filler counts are 2-3x the real number.

**Why it happens:**
Naive substring matching or even simple token matching doesn't account for word boundaries, context, or legitimate usage. "Like" as a filler ("I was, like, really nervous") vs "like" as a verb ("I would like to") vs "like" as a preposition ("It's like a marathon") — only the first is a filler. Simple matching counts all of them.

**How to avoid:**
- **Use spaCy with POS tagging and dependency parsing** to distinguish filler usage. For "like": match only when it's a discourse marker (typically INTJ tag or used parenthetically), not a verb (VB) or preposition (IN).
- **Use word boundaries in regex** — `\bum\b` not `"um" in word`.
- **Build a focused filler word list for interviews only** — "um", "uh", "er", "ah", "like" (discourse marker only), "basically" (sentence starter), "literally", "you know" (multi-word), "I mean" (multi-word), "sort of", "kind of".
- **For multi-word fillers** ("you know", "sort of"), use phrase-level detection with spaCy's `Matcher` or `PhraseMatcher`.
- **Consider matching against a list of "not-filler" patterns** — if "like" is followed by "to" (infinitive), it's not a filler.

**Warning signs:**
- "Umbrella" counts as using "um"
- "Likely" counts as using "like"
- Filler percentage > 25% of all words
- Common words like "basically" and "literally" always count even when used correctly

**Phase to address:**
Phase 3 (Transcript analysis — filler words + NLP)

---

### Pitfall 13: No Progress Feedback During Long Processing — User Abandons the App

**What goes wrong:**
The user uploads a 15-minute interview video and clicks "Analyze." The screen shows a generic spinner for 20+ minutes with no indication of what's happening, how long it will take, or whether the app is still working. The user assumes the app froze, closes the tab, and never returns.

**Why it happens:**
Streamlit doesn't natively support background task execution. The default pattern is: user clicks button → long blocking operation → page rerenders with results. During the blocking operation, there's no way to update the UI without using `st.empty()` + manual loop-based progress or `st.progress()`. Most tutorials don't cover this pattern. (Source: Streamlit docs on progress, Streamlit community patterns.)

**How to avoid:**
- **Use `st.progress()` within a loop** — update it after each processing stage completes (0-33% for transcription, 34-66% for video analysis, 67-100% for report generation).
- **Use `st.status()` with expanded details** — show "Transcribing audio... (5/10 minutes)", then collapse to "✅ Transcription complete" and show next stage.
- **Break the pipeline into named stages** -> emit stage names and progress percentages.
- **Use Python generators** to yield progress updates from processing functions.
- **Worst case** — even a simple "Processing... this usually takes ~X minutes" message is better than a silent spinner.
- **Avoid blocking the event loop entirely** — use `threading` or `concurrent.futures` for the processing task and poll for completion.

**Warning signs:**
- Only `st.spinner()` used, no progress granularity
- UI shows no indication of which stage is running
- Developer has to say "just wait, it's working" during demos
- No estimated time remaining

**Phase to address:**
Phase 4 (Dashboard/UI) — But requires the pipeline to expose progress hooks, which must be designed in Phase 1.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded landmark indices (33, 263, etc.) | Quick to write, no setup needed | Breaks on MediaPipe version update; requires full validation of all indices | Never — use named constants from day one |
| OpenCV Haar cascade for all face detection | Simple, no dependencies | Less robust than MediaPipe at angles/lighting; more false negatives | Only as pre-filter before MediaPipe (two-stage) |
| `openai/whisper` instead of `faster-whisper` | Simplest pip install | 4x slower transcription on CPU forever | Never for CPU-only deployment |
| `DeepFace.analyze()` default settings on every frame | One-liner code | Hours of CPU time per video; user abandons app | Never — always use keyframe sampling |
| No VAD preprocessing | Saves 10 lines of code | Hallucinated transcript destroys all downstream metrics | Never |
| Sequential blocking pipeline | Simple control flow | No user feedback; CPU underutilized; hard to cancel | Only if processing time < 30 seconds |
| Storing uploaded video in `st.session_state` | Accessible everywhere | Out-of-memory crash on large files | Never — write to disk immediately |
| Magic number confidence weights | Quick to iterate | Opaque scoring; impossible to debug or tune | Only as a placeholder in MVP, must be replaced before shipping |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenCV ↔ MediaPipe | Feeding BGR frames to MediaPipe (it expects RGB) | Always convert: `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)` before `face_mesh.process()` |
| MoviePy ↔ Whisper | Saving audio as MP3 (lossy compression can degrade Whisper accuracy) | Save as 16kHz mono WAV: Whisper internally resamples to 16kHz anyway, but avoid additional compression artifacts |
| Streamlit ↔ OpenCV VideoCapture | VideoCapture object left open across reruns, camera port locked | Use `cap.release()` in `finally` block; use `st.cache_resource` for the capture if needed |
| DeepFace ↔ Streamlit | Calling `DeepFace.analyze()` inside a cached function with `hash_funcs` not configured | Use `@st.cache_resource` for DeepFace models, `@st.cache_data` for results with proper `hash_funcs` |
| spaCy ↔ Whisper | Running full spaCy pipeline (NER, parser, tagger) when only tokenization + POS tagging needed | Use `nlp.select_pipes(enable=["tagger", "tokenizer"])` to exclude NER/parser — saves 40-60% inference time |
| Whisper ↔ VAD | Transcribing already-VAD-processed audio but Whisper expects contiguous speech | VAD outputs segments; concatenate them with minimal gaps (not silence) before passing to Whisper |
| FFmpeg ↔ Windows paths | Paths with spaces or Unicode characters break FFmpeg subprocess calls | Use `shlex.quote()` or pass paths as `Path` objects; test with spaces in filename |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all frames from video into memory at once | RAM spikes to multi-GB; app crashes | Process frames in a streaming loop: `while cap.isOpened(): ret, frame = cap.read()` | With any video > 100MB on an 8GB machine |
| `DeepFace.analyze()` on every frame | Takes 10+ hours for 10-min video | Sample 1 fps; aggregate emotions in windows | Always — this breaks at any scale |
| Using HuggingFace pipeline for Whisper | 5x slower than PyTorch, 10x slower than faster-whisper | Use `faster-whisper` directly | Always on CPU |
| Loading spaCy model inside a Streamlit loop | Model loads on every rerun (3-5 seconds each) | Cache with `@st.cache_resource` | On any rerun (button click, slider change) |
| `st.dataframe()` with 10k+ transcribed words | UI lag on every scroll/rerun | Use `st.dataframe` with `height` limit or paginate results | With any interview longer than a few minutes |
| Extracting audio with MoviePy's `AudioFileClip` as `np.array` | Extracts entire audio into NumPy array (RAM: ~10MB/min of audio) | Write to WAV file, then read in chunks for Whisper | With videos > 20 minutes |
| Temp file cleanup only on graceful shutdown | Temp files accumulate if process killed or crashes | Clean stale temp files on startup; always use `try/finally` | With frequent app restarts or crashes |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress indication during processing | User closes tab; assumes app broken | Show stage-by-stage progress with estimated time; use `st.progress()` + `st.status()` |
| Confidence score as a single opaque number | User can't interpret or trust the score | Show breakdown: "Eye contact: 16/25, Fillers: 8/25, Pace: 12/25 → Total: 36/75" |
| No explanation of what metrics mean | User doesn't know what "good" looks like | Add tooltips: "WPM > 160 is fast, < 120 is slow, 120-160 is ideal" |
| Emotion graph with sharp frame-to-frame changes | Looks chaotic, undermines credibility | Smooth with rolling window; show confidence bands |
| No way to re-watch specific parts of the video | User can't verify analysis claims | Link transcript timestamps to video position; show synchronized playback |
| Upload button says nothing about file size/time expectations | User uploads huge files expecting instant results | Show size limits, estimated processing time, and supported formats before upload |
| Analysis results shown without context | User can't tell if their scores are good or bad | Include benchmarks/norms: "Better than 65% of candidates" or target ranges |

## "Looks Done But Isn't" Checklist

- [ ] **Whisper transcription:** Often missing VAD preprocessing — verify that a 5-second silence in the audio produces an empty transcript segment (not hallucinated text)
- [ ] **Eye contact detection:** Often just "face detected" boolean — verify by turning your head 45° away from camera and checking that score drops
- [ ] **Emotion analysis:** Often reports "neutral" for everything — verify with a visibly angry/happy/surprised face and check that the correct emotion appears with reasonable confidence
- [ ] **Filler word count:** Often uses substring match — verify "umbrella" doesn't count as "um", and "like" as a verb doesn't count as filler
- [ ] **Processing progress:** Often shows a single spinner throughout — verify by timing the full pipeline and ensuring progress updates at least every 30 seconds
- [ ] **Memory cleanup:** Often leaks temp files — verify by running 3 analyses in a row and checking that temp directory hasn't grown by >500MB
- [ ] **Streamlit caching:** Often loads models on every interaction — verify by clicking a checkbox _after_ analysis completes and checking console logs for model re-loading
- [ ] **Error handling for corrupt videos:** Often assumes valid input — verify by uploading a 0-byte file, a corrupt MP4, and an unsupported format; each should show a user-friendly error, not a traceback

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Whisper hallucination on silence | MEDIUM | Add VAD preprocessing; re-transcribe all audio; re-compute WPM and filler counts |
| Streaming all frames through DeepFace | HIGH | Add frame sampling; re-run emotion analysis on keyframes; throw away old full-frame results |
| Streamlit OOM from large files | MEDIUM | Add disk-based file handling; the app already crashed, so user must re-upload |
| Wrong MediaPipe API version | HIGH (near rewrite) | Switch to `FaceLandmarker` (new API) or pin version to legacy; re-validate all landmark indices |
| Confidence score that users don't trust | MEDIUM | Add score breakdown UI; recalibrate weights; no data loss, but trust must be rebuilt |
| Cached stale results shown to user | LOW | Clear `st.cache_data` and `st.session_state`; re-run analysis |
| Accumulated temp files filling disk | LOW | Add startup cleanup script; delete files in `%TEMP%` older than 1 hour |
| Filler word detection via simple `in` check | MEDIUM | Replace with spaCy-based detection; re-run NLP on existing transcripts (no video re-analysis needed) |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Whisper hallucination (Pitfall 1) | Phase 1 (Audio/Whisper pipeline) | Test with 5-second silence gap → verify empty transcript output |
| Using wrong Whisper backend (Pitfall 2) | Phase 0 (Stack setup) | Verify `faster-whisper` is in requirements.txt, not `openai-whisper` |
| Frame-by-frame DeepFace (Pitfall 3) | Phase 2 (Video analysis architecture) | Verify max 1fps sampling rate; measure total processing time < video duration |
| Streamlit file memory crash (Pitfall 4) | Phase 1 (File upload + handling) | Test with 500MB video file → verify no OOM, file saves to disk |
| Full pipeline rerun on interaction (Pitfall 5) | Phase 4 (Dashboard/UI integration) | Click a button after analysis → verify no model re-loads in console |
| Wrong eye contact metric (Pitfall 6) | Phase 2 (MediaPipe analysis) | Turn head 45° → verify eye contact score drops significantly |
| Opaque confidence score (Pitfall 7) | Phase 3 (Heuristic scoring) | Verify UI shows score breakdown with component labels and targets |
| Emotion on keyframes misses transitions (Pitfall 8) | Phase 2-3 (DeepFace + feedback) | Test with video of person going happy→sad→angry → verify chart shows transitions |
| Temp file accumulation (Pitfall 9) | Phase 1 (File handling) | Run 3 analyses back-to-back → verify temp dir didn't grow >500MB |
| Sequential blocking pipeline (Pitfall 10) | Phase 1 (Pipeline architecture) | Measure end-to-end time vs sum of individual stages — verify overlap |
| Wrong MediaPipe API (Pitfall 11) | Phase 0 (Setup) | Verify landmark indices match expected positions for eyes, nose, mouth |
| Naive filler word detection (Pitfall 12) | Phase 3 (NLP analysis) | Test sentence "I would like to run" → verify "like" NOT counted as filler |
| No progress feedback (Pitfall 13) | Phase 4 (Dashboard/UI) | Start analysis → verify progress updates appear every <30 seconds |

## Sources

- OpenAI Whisper GitHub — Hallucination discussions, CPU inference notes, `no_speech_prob` docs
- SYSTRAN/faster-whisper GitHub — Benchmarks, CTranslate2 INT8 CPU optimization, 4x speedup claims
- PyPI faster-whisper page — Official speed/memory benchmarks
- MediaPipe official Face Mesh docs (google-ai-edge) — API version changes, 468→478 landmarks, BlazeFace pipeline
- Sander de Snaijer's MediaPipe landmark visual guide — Correct landmark index reference for 478-point model
- Streamlit GitHub issues #9218, #9460 — Large file upload crashes, chunked upload feature requests
- Streamlit Discuss "Memory usage when uploading new files" (#75511) — Memory accumulation bug reports
- Streamlit performance FAQ (#64007) — Caching patterns, `@st.cache_resource` vs `@st.cache_data`
- DeepFace GitHub issues #937 — CPU slowness, model pre-warming advice
- Stack Overflow "Speed up real-time face detection using CV2 and DeepFace" — CPU-only performance reports (~3.6s per detection)
- Calm-Whisper (Interspeech 2025) — Academic paper on Whisper hallucination reduction
- MoviePy GitHub issues #1940 — Temp files not cleaned up
- OpenCV VideoCapture release issues (GitHub #16929) — Windows camera not releasing
- ArXiv 2505.12969 — Whisper hallucination analysis on non-speech segments

---

*Pitfalls research for: AI Interview Analyzer (local video-based interview analysis)*
*Researched: 2026-05-16*
