# Directive: Authentication

## Objective
Implement secure user registration, login, JWT-based session management, and Google OAuth so that users can access their accounts safely.

## Inputs
- **Registration:** email, password, name
- **Login:** email, password
- **OAuth:** Google authorization code
- **Token refresh:** refresh token

## Outputs
- Hashed password stored in database
- JWT access token (short-lived)
- JWT refresh token (long-lived)
- User session object
- OAuth profile data merged with local account

## Required Tools / Scripts
- `execution/hash_password.py` — Bcrypt hashing and verification
- `execution/generate_jwt.py` — Create access and refresh tokens
- `execution/verify_jwt.py` — Decode and validate JWT tokens
- `execution/google_oauth_handler.py` — Exchange auth code, fetch profile

## Edge Cases
- Duplicate email registration — return 409 Conflict
- Invalid password format (< 8 chars) — reject at validation layer
- Expired JWT — return 401, client must use refresh token
- Expired refresh token — return 401, user must re-login
- Google account with no email — reject with clear message
- Google account already linked to another local account — merge or reject based on policy
- Brute-force login attempts — defer to `execution/rate_limit.py`

## Validation Rules
- [ ] Passwords are never stored in plaintext
- [ ] Bcrypt cost factor ≥ 12
- [ ] JWT access tokens expire in ≤ 30 minutes
- [ ] JWT refresh tokens expire in ≤ 7 days
- [ ] All auth endpoints are rate-limited
- [ ] CSRF protection is active on state-changing endpoints
- [ ] OAuth state parameter is validated to prevent CSRF
- [ ] Failed login returns generic error (no user enumeration)
