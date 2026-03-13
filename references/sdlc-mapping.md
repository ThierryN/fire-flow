# SDLC Flowchart → Dominion Flow Mapping

Source: Greg Balajewicz's generic SDLC flowchart (3-page swimlane diagram)

---

## SDLC Structure

```
Page 1: DEV PROCESS (Devs lane)
  Feature branch → unit test → merge develop into feature → integration test
  → "All works?" gate → discuss with team → wait for develop readiness
  → PR merge → deploy to DEV → go to QA

Page 2: QA/RELEASE PROCESS (QA + DevOps lanes)
  Refresh QA from prod → cut release branch → smoke test → full QA testing
  → "Bugs found?" loop (fix → retest → re-assess scope → continue)
  → QA sign-off → refresh staging from prod → test staging
  → "Bugs found on staging?" → go BACK to QA (never fix on staging)
  → release to prod → sanity check

Page 3: POST-PROD (Devs lane)
  Check error logs → check perf logs → done
```

---

## Key SDLC Patterns and Dominion Flow Equivalents

| SDLC Pattern | Dominion Flow Equivalent | Status |
|-------------|------------------------|--------|
| Feature branch + unit test | `/fire-3-execute` (breath execution) | Strong |
| "All works?" gate | Must-haves verification | Strong |
| Merge to develop via PR | Atomic commits per task | Strong |
| QA testing + bug loop | `/fire-4-verify` (70-point) | Improved v11.3 |
| "Assess scope of retest" | Scope-adaptive checklist (v11.3) | Added v11.3 |
| "No fixes on staging" | Verifier isolation (fresh instance) | Strong |
| "Bugs found?" → fix → retest | Recovery research loop | Improved v11.3 |
| Post-prod: error/perf logs | Not yet implemented | Future |
| Branch readiness gate | Phase dependency gates | Strong |
| Sanity check on prod | Post-deploy verification | Future |

---

## Critical SDLC Insight: The "Bugs Found?" Diamond

The most important shape on the SDLC chart is the "Bugs found?" diamond. It appears at:
- DEV: "All works?" → No → loop back to fix
- QA: "Bugs found?" → Yes → fix → retest (scoped, not full regression)
- Staging: "Bugs found?" → Yes → go BACK to QA (never fix on staging)

**The diamond is a roundabout, not a stop sign.**

In Dominion Flow v11.3, this maps to:
- Circuit breaker trip → spawn fire-researcher → get alternatives → re-plan → retry
- Verification FAIL → recovery research → re-plan with different approach → re-execute
- Low confidence → research first → then proceed with givens

---

## SDLC Rules Applied to Dominion Flow

1. **"No fixes on staging"** = Verifier runs in isolation. If it finds bugs, it sends you BACK to execute (via re-plan), never patches in place.

2. **"Assess scope of retest"** = 70-point checklist is scope-adaptive. Backend change? Skip E2E/mobile/bundle checks. Config change? Minimal verification.

3. **"Bugs found? → fix → retest loop"** = Circuit breaker trips route to fire-researcher, not just escalation. The loop continues until resolved or max attempts exhausted.

4. **"Post-prod monitoring"** = Future: add error log + perf check step after deployment.

---

*Reference for Dominion Flow architecture decisions. Source: github.com/GregBalajewicz/SDLC-flow-chart*
