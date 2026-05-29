# MVP Polish Log

Last updated: 2026-05-27

This file tracks small bugs, rough edges, and post-MVP improvements so they do not get lost while we focus on shipping the first private deployment.

Priority guide:
- P0: blocks deployment or breaks core flow
- P1: serious MVP issue to fix before real users
- P2: should fix before wider testing
- P3: polish or post-MVP improvement

Status guide:
- Not started
- In progress
- Needs test
- Passed
- Parked for post-MVP

## Current MVP Gate

### Admin dashboard
- Status: Mostly working
- Priority: P1
- Notes:
  - Leads page is working.
  - Lead detail is working.
  - Admin token flow needed debugging before and should be checked once more before deployment.
  - Dashboard should only show real backend-supported data.

### Manual end-to-end flow testing
- Status: In progress
- Priority: P1
- Notes:
  - `backend/tests/manual_life_flow.py` now supports multiple scenario tests.
  - Keep pasting transcripts into our workflow and log every routing, extraction, or UX issue here.

### AWS deployment prep
- Status: Not started
- Priority: P1
- Notes:
  - Do this after local MVP flow checks are stable.
  - Need backend env config, frontend API URL config, persistent database choice, and deployment smoke test.

## Manual Flow Issues

### Quote explanation routing
- Status: Passed
- Priority: P3
- Notes:
  - Quote explanation now routes to `explanation`.
  - It uses the real quote and real answered fields.
  - Response is a little generic and repetitive.
- Future fix:
  - Make explanations more structured:
    - lower-price factors
    - higher-price factors
    - what could change the estimate
    - broker review disclaimer

### Broker handoff after quote
- Status: Passed
- Priority: P3
- Notes:
  - `broker_handoff` passed.
  - "Can I talk to a broker?" routed to `meeting`.
  - Contact info persisted to admin detail.
  - Meeting status showed `sent`.
  - Lead quality showed `high`.
  - Minor polish: contact prompt is functional but stiff: "Please provide your name so we can schedule your meeting."
- Future fix:
  - Make contact collection feel warmer and less robotic, while still asking for one missing field at a time.

### Broker handoff before completed quote
- Status: Passed
- Priority: P3
- Notes:
  - `meeting_before_quote` passed.
  - User asked for a broker after only age and gender.
  - Request routed to `meeting`.
  - Contact info persisted.
  - Meeting status showed `sent`.
  - Quote stayed `None`, which is correct because intake was incomplete.
  - Missing underwriting fields remained visible in admin detail.
  - Lead quality showed `high` because the user provided contact info and requested broker follow-up.
- Future fix:
  - Consider showing a separate "High intent, incomplete intake" label in the admin UI so brokers understand this lead is interested but still missing quote data.

### Correction flow
- Status: Passed
- Priority: P3
- Notes:
  - `correction` passed for coverage amount change.
  - User changed coverage from `$500,000` to `$750,000`.
  - Application updated existing `coverage_amount`.
  - Quote recalculated from about `$42/month` to about `$63/month`.
  - Follow-up explanation correctly referenced the increased coverage amount.
  - Admin summary reflected the updated `$750,000` coverage.
- Future fix:
  - Test corrections for term length, smoker status, and health condition changes.
  - Polish wording so the assistant avoids generic lines like "These elements collectively influence..."

### Invalid coverage or term values
- Status: Passed
- Priority: P3
- Notes:
  - `invalid_options` passed.
  - User asked for `$300k` coverage and `25` years.
  - System did not silently snap unsupported values to valid values.
  - `coverage_amount` and `term_length` remained missing.
  - Quote stayed `None`.
  - Bot guided the user back to supported choices.
- Future fix:
  - Wording polish: "Which amounts would you like to choose?" should become something clearer like "Which coverage amount and term length would you like to use?"

### BMI extraction
- Status: Passed for clean flow
- Priority: P2
- Notes:
  - "5 foot 10 and 180 pounds" now extracts BMI correctly in the clean flow.
  - Still test messy variants like `5'9 maybe 175`, `five ten 180`, and `180 lbs, 5 10`.

### Health history question timing
- Status: Needs review
- Priority: P3
- Notes:
  - The assistant sometimes asks family history before collecting health conditions, depending on turn order.
  - This is not broken, but the flow should feel consistent and broker-like.

### Repeated or generic assistant wording
- Status: Not started
- Priority: P3
- Notes:
  - Several responses are correct but generic.
  - Examples:
    - "These factors collectively influence the estimate"
    - "Final premiums would require underwriting review"
  - Improve tone after core MVP is stable.

### Privacy objection flow
- Status: Passed
- Priority: P3
- Notes:
  - `privacy` originally found a real issue.
  - Fixed and retested.
  - Good:
    - Bot respected the user's reluctance to share name.
    - Bot correctly said a name is not needed for a quote.
    - Bot now stops asking health/family-history questions after a health-question refusal.
    - Bot explains the estimate is preliminary and offers broker handoff.
    - Bot does not mark application `completed`.
    - Missing fields remain visible.
    - Admin lead quality now says meaningful progress, not complete quote intake.
- Future fix:
  - Polish privacy copy in the public widget so users understand what data is used for before they reach this point.

### Messy natural-language intake
- Status: Passed
- Priority: P3
- Notes:
  - `messy` originally found real issues.
  - Fixed and retested.
  - Good:
    - Slangy intro worked.
    - `im like 29, guy` extracted age and gender.
    - `5'9 maybe 175` extracted BMI.
    - `half a mil sounds fine maybe 20 years` extracted coverage and term.
    - Contact info eventually persisted to admin.
    - `yeah send this to someone` now routes to `meeting`.
    - Incomplete fields stay visible.
    - `completed` stays false when `family_history_count` and `zip_risk` are missing.
    - Admin lead quality now says meaningful progress, not complete quote intake.
- Future fix:
  - Decide whether city/area inputs should be accepted for risk lookup later, or whether the assistant should ask for ZIP/risk explicitly.

## Admin Dashboard Issues

### Lead detail completeness
- Status: Mostly working
- Priority: P2
- Notes:
  - Lead detail should clearly show:
    - name
    - email
    - phone
    - meeting status
    - quote
    - missing fields
    - answered fields
    - chat history
    - summary
    - DEC page review if present

### Admin empty states
- Status: Needs review
- Priority: P2
- Notes:
  - Pages should look intentional when there are no leads, no DEC page, no messages, or no quote.
  - Empty states should not claim fake activity.

### Admin dashboard visual polish
- Status: In progress
- Priority: P2
- Notes:
  - Matte black and gold direction is the desired design system.
  - Must feel like operational underwriting software, not a marketing site.
  - Keep dense, readable, broker-focused tables.

### Disabled navigation sections
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - Sidebar can show future sections as disabled or "Soon":
    - Applications
    - Quotes
    - Underwriting
    - Clients
    - Reports
    - Settings
  - Do not fake functionality behind these yet.

### Broker notes and status editing
- Status: Parked for post-MVP
- Priority: P2
- Notes:
  - Useful future feature.
  - Admin should eventually let broker add notes, set lead status, and track follow-up state.
  - Out of scope for current read-only dashboard.

### LLM summary quality
- Status: Needs review
- Priority: P2
- Notes:
  - Admin summary is useful but should be checked for missing details, hallucinated details, and overly long output.
  - Summary should help a broker decide what to do next quickly.

## Backend/API Issues

### Admin auth final check
- Status: Needs test
- Priority: P1
- Notes:
  - Confirm wrong token returns `401`.
  - Confirm missing token returns `401`.
  - Confirm correct token returns lead data.

### `/admin/leads` empty database behavior
- Status: Needs test
- Priority: P1
- Notes:
  - Should return `[]`, not `500`.

### `/admin/leads/{session_id}` unknown session behavior
- Status: Needs test
- Priority: P1
- Notes:
  - Should return `404`, not `500`.

### SQLite path and env behavior
- Status: Mostly fixed
- Priority: P1
- Notes:
  - Database URL handling was cleaned up.
  - Recheck before deployment so local and production do not accidentally use different databases.

### Model path behavior
- Status: Needs deployment review
- Priority: P1
- Notes:
  - Ensure ML model files load correctly from deployed backend.
  - Backend should not depend on a laptop-local path.

### Backend smoke test
- Status: Not started
- Priority: P1
- Notes:
  - Add or run a lightweight smoke test before deployment:
    - health check
    - create account
    - create session
    - send chat message
    - admin protected endpoint

### Quote history
- Status: Needs review
- Priority: P2
- Notes:
  - Backend-supported quote history exists conceptually.
  - Confirm what is actually stored and exposed before building richer UI around it.

### Underwriting summaries
- Status: Needs review
- Priority: P2
- Notes:
  - Useful for admin.
  - Need to verify current data source and avoid fake summaries.

## Frontend/UI Issues

### Chat widget trust messaging
- Status: Not started
- Priority: P2
- Notes:
  - Users may feel nervous sharing insurance details with AI.
  - Add concise trust copy near upload/intake moments.
  - Avoid over-explaining or making it feel scary.

### Consent before document upload
- Status: Not started
- Priority: P2
- Notes:
  - Before DEC page upload, explain what is being reviewed and why.
  - Make it clear upload is optional for the quote workflow if that is true.

### Contact handoff copy
- Status: Not started
- Priority: P2
- Notes:
  - Broker handoff should feel natural and low pressure.
  - Goal is to nudge users toward a broker meeting without forcing it.

### Existing chat outside admin
- Status: Needs regression test
- Priority: P1
- Notes:
  - Admin routing changes should not break the public chat widget.

### Mobile responsive check
- Status: Not started
- Priority: P2
- Notes:
  - Need to verify public widget and admin dashboard at mobile widths.
  - Text should not overlap or overflow.

## Anti-Spam And Lead Quality

### Basic spam controls
- Status: Not started
- Priority: P1
- Notes:
  - Needed before putting on real websites.
  - Consider basic rate limiting, request size limits, and obvious fake contact detection.

### Lead quality rules
- Status: Implemented, needs more test
- Priority: P2
- Notes:
  - Current quality levels:
    - high
    - medium
    - low
  - Needs real transcript testing to see if reasons are useful to brokers.

### Fake info detection
- Status: Not started
- Priority: P2
- Notes:
  - Do not overbuild yet.
  - Start simple:
    - missing contact
    - invalid-looking phone
    - disposable-looking email if easy
    - very short or nonsense messages

## Document Review

### DEC page value proposition
- Status: Parked for post-MVP
- Priority: P2
- Notes:
  - Original goal: find holes and suggest what could be better.
  - Should nudge user to meet broker without forcing them.

### Document review output quality
- Status: Needs test
- Priority: P2
- Notes:
  - Need sample DEC page tests.
  - Output should identify coverage gaps or review points without making unsupported legal/insurance claims.

### DEC page admin view
- Status: Needs review
- Priority: P2
- Notes:
  - Admin detail should show parsed DEC data or a clean empty state.

## Privacy And Compliance Polish

### User comfort with personal insurance info
- Status: Not started
- Priority: P2
- Notes:
  - Add calm copy that explains:
    - what info is used for
    - that estimate is preliminary
    - licensed broker handles next steps
  - Avoid asking for SSN or highly sensitive data in MVP.

### Estimate disclaimer
- Status: Needs review
- Priority: P2
- Notes:
  - Quote should be clearly positioned as an estimate.
  - Final premium depends on underwriting/carrier review.

### Data retention policy
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - Eventually need a clear answer for how long lead/chat/document data is stored.

## Deployment

### Production environment variables
- Status: Not started
- Priority: P1
- Notes:
  - Need production values for:
    - `ADMIN_TOKEN`
    - `DATABASE_URL`
    - LLM/API keys
    - frontend API base URL
    - CORS origins

### Database choice for AWS MVP
- Status: Not started
- Priority: P1
- Notes:
  - Decide whether MVP uses SQLite on a persistent volume or Postgres/RDS.
  - For real users, avoid losing data across deploys/restarts.

### Frontend deployment target
- Status: Not started
- Priority: P1
- Notes:
  - Need a deployed admin URL and embeddable/public widget URL.

### Real website embed
- Status: Not started
- Priority: P1
- Notes:
  - This product needs to work as a website bubble/widget.
  - Need test deployment on friend's dad's website or another small site.

### Safe editing after deployment
- Status: Not started
- Priority: P1
- Notes:
  - Need a simple deployment workflow:
    - local development
    - test locally
    - push/deploy
    - avoid editing production directly

## Post-MVP Product Upgrades

### Consumer-first flow
- Status: Parked for post-MVP
- Priority: P2
- Notes:
  - Current MVP can ship first.
  - Later improve flow to feel more consumer-first and less form-like.

### Better AI workflow assistant
- Status: Parked for post-MVP
- Priority: P2
- Notes:
  - Improve assistant from basic intake into a stronger insurance workflow:
    - explain tradeoffs
    - compare coverage choices
    - summarize next steps
    - help broker prepare for call

### PolicyBazaar-inspired comparison experience
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - Do not clone PolicyBazaar directly.
  - Possible future direction:
    - guided quote journey
    - side-by-side plan options if real data exists
    - broker-assisted recommendation

### Multi-insurance expansion
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - Life insurance is the proof of concept.
  - Only expand after life workflow is strong.
  - Future lines:
    - Auto
    - Home
    - Renters
    - Health

### Bigger agency workflows
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - Small brokers may not have enough traffic.
  - Later, larger agencies may need:
    - multiple broker accounts
    - agency separation
    - assignment queues
    - lead ownership
    - reporting

### Broker outreach wave two
- Status: Parked for post-MVP
- Priority: P3
- Notes:
  - First deploy to known small websites and people you know.
  - After polish, start LinkedIn broker outreach with a better demo.
