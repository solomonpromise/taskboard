# ADR 005: Server-side sessions in HttpOnly cookies, with CSRF tokens
Date: 2026-11-05 · Status: Accepted

**Context.** Browser-only client on the same origin; sign-out must take effect immediately.
**Options.** Server sessions in cookies; JWT access tokens in browser storage; hosted auth service.
**Decision.** Random session token in an HttpOnly, Secure (in production), SameSite=Lax cookie;
only its hash is stored. Per-session CSRF token sent in `X-CSRF-Token` on changes. Passwords hashed
with Argon2 (pwdlib); policy per NIST SP 800-63B-4.
**Consequences.** Revocable sessions, no tokens readable by scripts; we own password storage, so
password reset and MFA are on the roadmap. A hosted auth service remains an option.
**Revisit if.** We add a mobile app (consider tokens) or need SSO/MFA quickly (consider a service).
