# Directive: Security Hardening

## Objective
Protect the application from common web vulnerabilities and ensure all data, endpoints, and secrets are properly secured.

## Inputs
- All incoming HTTP requests
- All user-submitted data
- All environment configuration

## Outputs
- Sanitised inputs
- Rate-limited endpoints
- Structured error logs (no sensitive data leaked)
- Secure HTTP headers

## Required Tools / Scripts
- `execution/input_sanitization.py` — Strip XSS, SQL injection, and malicious input
- `execution/rate_limit.py` — Per-IP and per-user rate limiting
- `execution/error_logger.py` — Structured logging with severity levels

## Security Requirements

### Transport
- HTTPS only in production
- HSTS header enabled
- Secure cookie flags (HttpOnly, Secure, SameSite)

### Input Validation
- All inputs sanitised before processing
- SQL queries use parameterised statements only (SQLAlchemy ORM)
- HTML output escaped to prevent XSS

### Authentication & Authorization
- API routes require valid JWT
- Admin routes require `role: admin` in JWT
- CSRF tokens on all state-changing requests
- Session fixation prevention

### Rate Limiting
- Login: 5 attempts / 15 minutes per IP
- API: 60 requests / minute per user
- Registration: 3 accounts / hour per IP

### Error Handling
- Never expose stack traces to client
- Log full details server-side
- Return generic error messages to users

## Edge Cases
- Rate limit hit — return 429 with `Retry-After` header
- Malformed JWT — return 401 (not 500)
- Database connection loss — return 503, log, and alert

## Validation Rules
- [ ] No raw SQL queries anywhere in codebase
- [ ] All API endpoints have authentication middleware
- [ ] Rate limiting active on all public endpoints
- [ ] Error responses never contain stack traces or internal details
- [ ] `.env` is in `.gitignore` and never committed
- [ ] CORS is configured to allow only known origins
