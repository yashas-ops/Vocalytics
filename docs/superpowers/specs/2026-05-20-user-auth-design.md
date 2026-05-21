# User Authentication System — Design Spec

## Overview

Add a full multi-user authentication system to the AI Interview Analyzer. Users can register, log in, and log out. Each user sees only their own interview sessions. The auth UI reuses the existing Read.cv-inspired editorial theme.

## Database Changes

### New `users` table (in `database/init.py`)

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### Migration: Add `user_id` to `interviews`

```sql
ALTER TABLE interviews ADD COLUMN user_id INTEGER DEFAULT NULL;
```

Nullable for backward compatibility — existing anonymous interviews remain visible. Follows the same pattern as `migrate_add_candidate_fields`.

### New DB functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `create_user(username, password_hash)` | int (user_id) | Insert new user |
| `fetch_user_by_username(username)` | dict or None | Lookup by username |
| `fetch_user_by_id(user_id)` | dict or None | Lookup by ID |
| `fetch_interviews_by_user(user_id)` | list | Filtered interviews |

`fetch_all_interviews()` stays unchanged for internal use.

## Auth Module (`modules/auth.py`)

Pure stdlib — no new dependencies.

| Function | Returns | Purpose |
|----------|---------|---------|
| `hash_password(password)` | str (`salt$hash`) | 16-byte random salt + SHA-256 |
| `verify_password(password, stored)` | bool | Constant-time comparison |
| `register_user(username, password)` | `(bool, str)` | Validates length/uniqueness, hashes, stores |
| `authenticate_user(username, password)` | `int or None` | Returns user_id on success |
| `logout_user()` | None | Clears session auth keys |

Constraints:
- Username: 3–30 chars, alphanumeric + underscores only
- Password: minimum 6 chars
- Username must be unique (case-insensitive via `.lower()`)

## Session State

New keys added to `initialize_session_state()`:

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `user_id` | int or None | None | Logged-in user's ID |
| `username` | str or None | None | Logged-in user's display name |

## Page Changes

### New pages

- **Login** (`render_login_page`): Centered form with username input, password input, "Sign in" button, link to Register page.
- **Register** (`render_register_page`): Same layout with confirm-password field, "Create account" button, link to Login page.

Both use existing `surface-hero` styling and Streamlit text inputs/buttons — no new CSS required.

### Auth gate

At the top of `app.py` after `initialize_session_state()` and `load_css()`:

```
if not st.session_state.user_id:
    if page not in ("Login", "Register"):
        st.session_state.page = "Login"
    render_login_page() or render_register_page()
    st.stop()
```

This prevents unauthenticated access to Upload/Dashboard/History.

### Navigation changes

- The main PAGES tuple stays `("Upload", "Dashboard", "History")` — only shown to auth users.
- Auth pages (`Login`, `Register`) are not in PAGES — they render standalone without top nav.
- **Logout** button added to sidebar (below theme toggle) — calls `logout_user()` and reruns.
- Top nav bar shows logged-in username on the right side (replaces "Latest session" with user context when appropriate).

### Interview ownership

- `insert_interview()` now accepts optional `user_id` param (default None)
- On upload, passes the current `st.session_state.user_id`
- History page uses `fetch_interviews_by_user(user_id)` instead of `fetch_all_interviews()`
- Old interviews with NULL `user_id` remain visible in history for backward compat

## No New Dependencies

All password hashing uses stdlib (`hashlib`, `os.urandom`, `secrets`). No additional pip packages.

## Error Handling

- Login failure: show error message "Invalid username or password"
- Registration failure (duplicate): show "Username already taken"
- Registration failure (validation): show specific message ("Password must be at least 6 characters", etc.)
- Logout: always succeeds, clears session, redirects to Login

## Testing

Manual verification plan:
1. Launch app → see Login page (not Upload) → no nav bar visible
2. Click "Register" → fill form → submit → redirect to Login
3. Login with new credentials → see Upload page with full nav
4. Sidebar shows username, logout button works
5. Upload an interview → it's owned by the user
6. Logout → cannot access pages without login
7. Register another user → separate interview lists
8. Old anonymous interviews still visible in history
