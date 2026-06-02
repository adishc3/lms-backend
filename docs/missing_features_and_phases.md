# Missing Features & Implementation Phases

This document lists the notable missing or partially-implemented LMS features and a concise phased plan to implement them.

## Missing / Partial Features

- Course progress tracking (per-user lesson completion, time tracking)
- Manual grading and assignments (submissions, rubrics, instructor grading)
- Certificates and badges (PDF issuance, verifiable IDs)
- Rich content editor (Markdown / WYSIWYG, media embedding, sanitization)
- Discussion forums and threaded comments
- Scheduling and drip-feed content (release dates, prerequisites)
- Payment & billing (pricing, subscriptions, gateway integration)
- Advanced analytics & reporting (engagement, weak-topic detection)
- Two-factor authentication (TOTP and optional SMS)
- API rate limiting and abuse protection
- Database migrations (Alembic) — added as Phase 15
- Search & discovery (full-text search, filters, recommendations)
- Mobile support (PWA or native clients)
- Multi-tenancy (organization/tenant isolation)
- In-app notifications and notification center

## Phased Implementation Plan (Concise)

Phase 15 — Migrations & Prod Readiness (blocking)
- Add Alembic scaffold and initial migration (capture current models).
- Effort: Medium (3–5 days).

Phase 16 — Security & Rate Limiting
- Add rate limiting middleware, input sanitization, CSRF protections, and basic WAF rules.
- Effort: Medium (3–4 days).

Phase 17 — Progress Tracking & Completion
- Implement `lesson_completions` model, APIs to mark completion, progress calculation, and instructor views.
- Effort: Large (5–7 days).

Phase 18 — Email Verification & Password Reset
- Implement verification tokens, reset flow, and ensure unverified users cannot enroll.
- Effort: Medium (3–4 days).

Phase 19 — Assignments & Manual Grading
- Add `assignments` and `submissions` models, instructor grading UI, and gradebook export.
- Effort: Large (6–8 days).

Phase 20 — Student Dashboard & UX
- Build student-facing dashboard showing enrolled courses, progress bars, due items, and quick actions.
- Effort: Large (6–8 days).

Phase 21 — Certificates & Badges
- Generate PDF certificates with unique IDs and badge-awarding logic for milestones.
- Effort: Large (5–7 days).

Phase 22 — Rich Content Editor
- Add Markdown/WYSIWYG editor, media uploads, and safe rendering pipeline.
- Effort: Large (6–8 days).

Phase 23 — Analytics & Reporting
- Add instructor analytics: completion rates, weak questions, cohort comparison, and exports.
- Effort: Large (7–9 days).

Phase 24 — Discussion Forums & Notifications
- Build forums with moderation tools and in-app notifications for replies and mentions.
- Effort: Large (7–9 days).

Phase 25 — Scheduling & Drip Content
- Add lesson release dates, prerequisites, and a scheduler to unlock content.
- Effort: Medium-Large (5–6 days).

Phase 26 — 2FA & Account Security
- Implement TOTP setup, backup codes, and optional SMS fallback.
- Effort: Medium (4–5 days).

Phase 27 — Search, Discovery & Recommendation
- Add full-text search, filters, and simple recommendations based on progress and interests.
- Effort: Medium (4–6 days).

Phase 28 — Mobile (PWA first)
- Implement PWA support for offline viewing and installable experience; consider native later.
- Effort: Very Large (10–20 days depending on scope).

Phase 29 — Multi-Tenancy
- Add `Organization` model, tenant isolation, and org-scoped admin UX.
- Effort: Very Large (10–15 days).

## Quick Priorities (first 4 actions)

1. Alembic migrations (Phase 15) — required for safe schema changes.
2. Rate limiting & sanitization (Phase 16) — protect public endpoints.
3. Progress tracking (Phase 17) — core LMS functionality.
4. Email verification (Phase 18) — user security and trust.

## Notes
- Each phase includes schema migration work where applicable. Use Alembic for all DB changes.
- Add tests for each new feature and include migration checks in CI.
- Prioritize security and data integrity before adding user-facing features.

---

File: [docs/implementation_phases.md](docs/implementation_phases.md) contains the full roadmap and detailed phase descriptions.
