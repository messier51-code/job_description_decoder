# Coaching State — Example Candidate
Last updated: 2026-09-29

## Profile
- Target role(s): Senior Software Engineer / Staff Backend Engineer
- Seniority band: Senior
- Track: Full System
- Feedback directness: 3
- Interview timeline: ongoing
- Time-aware coaching mode: triage
- Interview history: active but not advancing
- Biggest concern: system design depth under time pressure
- Known interview formats: behavioral screen, coding, system design
- Anxiety profile: anxious-specific
- Career transition: none
- Transition narrative status: not started

## Resume Analysis
- Positioning strengths: distributed systems ownership; Python/Go services at scale; mentoring mid-level engineers
- Likely interviewer concerns: limited public cloud certifications; fewer consumer-product brands on resume
- Career narrative gaps: IC → tech lead transition needs a crisp story
- Story seeds: multi-region failover rewrite; Kafka consumer lag incident; onboarding platform for new hires

## Storybank
| ID | Title | Primary Skill | Secondary Skill | Earned Secret | Strength | Use Count | Last Used |
|----|-------|---------------|-----------------|---------------|----------|-----------|-----------|
| S001 | Multi-region failover rewrite | Distributed systems | Incident response | Ship reliability before features when blast radius is large | Strong | 2 | 2026-08-01 |
| S002 | Kafka lag war room | Streaming data | Cross-team leadership | Lag is a symptom; ownership maps beat dashboards | Strong | 1 | 2026-07-12 |
| S003 | Onboarding platform | Platform engineering | Mentoring | Developer experience compounds hiring velocity | Medium | 0 | — |

### Story Details
#### S001 — Multi-region failover rewrite
- Situation: Primary region outages were causing multi-hour downtime for a payments API.
- Task: Lead rewrite of failover path without freezing feature delivery.
- Action: Designed active-passive cutover, load-tested failure modes, staged rollout with kill switches.
- Result: RTO dropped from 4h to <15m; zero customer-facing incidents in following two quarters.
- Earned Secret: Reliability work only sticks when product shares the risk budget.
- Deploy for: ownership under ambiguity; distributed systems depth
- Version history: 2026-06-01 — initial

#### S002 — Kafka lag war room
- Situation: Consumer lag spiked during a Black Friday–scale traffic event.
- Task: Restore processing and prevent order of magnitude backlog growth.
- Action: Coordinated three teams, partitioned hot keys, temporarily scaled consumers, added backpressure.
- Result: Cleared 12h backlog in 90 minutes; added permanent lag SLO alerts.
- Earned Secret: Cross-team war rooms need a single decision owner.
- Deploy for: leadership under pressure; streaming systems
- Version history: 2026-05-20 — initial

#### S003 — Onboarding platform
- Situation: New engineers took 3+ weeks to ship first PR.
- Task: Build internal onboarding platform and golden-path docs.
- Action: Automated env bootstrap, seeded starter services, paired mentoring rotations.
- Result: Time-to-first-PR fell to 4 days median.
- Earned Secret: Mentoring systems beat heroics.
- Deploy for: platform thinking; mentoring / tech lead signals
- Version history: 2026-04-10 — initial

## Score History
### Recent Scores
| Date | Type | Context | Sub | Str | Rel | Cred | Diff | Hire Signal | Self-Δ |
|------|------|---------|-----|-----|-----|------|------|-------------|--------|
| 2026-08-15 | practice | system design drill | 3 | 4 | 3 | 4 | 3 | | accurate |

## Outcome Log
| Date | Company | Role | Round | Result | Notes |
|------|---------|------|-------|--------|-------|
| 2026-08-20 | ExampleCo | Senior SWE | R1 | pending | Waiting on loop |

## JD Analysis
| Date | Company | Role | Fit | Top Competencies | Notes |
|------|---------|------|-----|------------------|-------|
