# UI Fix Round 2 — Implementation Plan

## Files to Modify

### 1. `assets/styles.css`

| Change | Old | New | Purpose |
|--------|-----|-----|---------|
| `.surface` padding | `1.1rem` | `1.25rem` | More breathing room in all cards |
| `.surface` margin-bottom | `0.95rem` | `1rem` | Consistent section gap |
| `.detail-list > div` padding | `0.75rem 0.9rem` | `1rem` | Standard card padding |
| `.detail-list > div` min-height | — | `60px` | Prevent collapsed cards |
| `.detail-list` gap | `0.62rem` | `0.75rem` | Align to spacing scale |
| `.insight-card` padding | `0.82rem 0.9rem` | `1rem` | Standard card padding |
| `.insight-grid` gap | `0.7rem` | `0.75rem` | Align to spacing scale |
| `.score-lockup` padding | `1.05rem` | `1.25rem` | More breathing room |
| `.checklist > div` padding | `0.82rem 0.9rem` | `1rem` | Standard card padding |
| `.checklist` gap | `0.68rem` | `0.75rem` | Align to spacing scale |
| `.file-summary > div` padding | `0.82rem 0.9rem` | `1rem` | Standard card padding |
| `.file-summary` gap | `0.7rem` | `0.75rem` | Align to spacing scale |
| `div[data-testid="stMetric"]` padding | `0.85rem 0.92rem` | `1rem` | Standard card padding |
| `div[data-testid="stMetric"]` min-height | — | `80px` | Prevent collapsed cards |
| `.section-header` margin-bottom | `0.95rem` | `0.75rem` | Tighter section spacing |
| `div[data-testid="stFileUploader"]` padding | `0.75rem` | `1rem` | Roomier upload area |
| `.process-strip` gap | `0.5rem` | `0.75rem` | Better step separation |
| `.process-strip` margin-bottom | `1rem` | `1.25rem` | More space after strip |
| `.process-strip span` min-height | `34px` | `38px` | Taller pills |
| `.process-strip span` padding | — | `0 0.75rem` | Horizontal padding for text |
| `.signal-strip > div` padding | `0.8rem 1rem` | `0.75rem 1rem` | Consistent vertical rhythm |

### 2. `app.py`

| Location | Change | Purpose |
|----------|--------|---------|
| `--muted-foreground` (light) | `#66706a` → `#555e59` | 4.6:1 WCAG AA contrast on muted bg |
| `--text-soft` (light) | `#8a9490` → `#7a8480` | Fix hierarchy inversion (was lighter than muted-foreground) |
| `color_continuous_scale` | Hardcoded → theme-aware | Light: `["#d4dcd6","#8a9e8e","#b6975d"]`, Dark: `["#2f332f","#6f8068","#b6a06a"]` |
| `fig_emotion.update_layout` | Add `font=dict(color=font_c)` | Set chart text color from theme |
| `fig_emotion.update_xaxes` | Add `tickfont=dict(color=tick_c)` | X-axis tick color from theme |
| `fig_emotion.update_yaxes` | Add `tickfont=dict(color=tick_c)` | Y-axis tick color from theme |
| `fig_emotion.update_traces` | Add `textfont=dict(color=font_c)` | Bar label color from theme |

### 3. `tests/test_app_shell.py`

| Location | Change | Purpose |
|----------|--------|---------|
| Line 70 | `#66706a` → `#555e59` | Match updated muted-foreground |
| Line 84–85 (if exists) | Adjust for soft → `#7a8480` | Match updated text-soft |

## Theme Color Hierarchy (Light Mode)

```
foreground      #171a19   (main text — darkest)
muted-foreground #555e59   (body/description text)
text-soft        #7a8480   (labels/captions — lightest)
```

This fixes the inversion where `text-soft` (#8a9490) was lighter than `muted-foreground` (#66706a).

## Graph Text Colors (Theme-aware variables in app.py)

```python
is_light = st.session_state.theme == "Light"
font_c = "#171a19" if is_light else "#eceeed"      # main text
tick_c = "#555e59" if is_light else "#8a8a8a"       # axis ticks
```

## Files NOT Modified

- Any module in `modules/`
- `database/`
- `utils/`
- `models/`
- Any API/business logic
- Upload/transcription/report pipeline
- Animations preserved as-is
