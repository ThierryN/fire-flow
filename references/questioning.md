# Dominion Flow Questioning Reference

> **Origin:** Ported from Dominion Flow `questioning.md` with SDLC-aware questioning additions.

## Philosophy

**You are a thinking partner, not an interviewer.** The user often has a fuzzy idea. Your job is to help them sharpen it. Ask questions that make them think "oh, I hadn't considered that" or "yes, that's exactly what I mean."

---

## The Goal

By the end of questioning, you need enough clarity to write a PROJECT.md:

- **Research:** What domain to research, what unknowns exist
- **Requirements:** Clear enough vision to scope v1 features
- **Roadmap:** Clear enough to decompose into phases
- **Testing:** Which flows are critical and require mandatory testing
- **Branch strategy:** Project complexity determines Git Flow depth
- **Blocker risks:** Known technical risks that might become blockers

---

## How to Question

- **Start open.** Let them dump their mental model.
- **Follow energy.** Whatever they emphasized, dig into that.
- **Challenge vagueness.** "Good" means what? "Users" means who?
- **Make abstract concrete.** "Walk me through using this."
- **Surface critical flows early.** Payment, auth, data mutation.
- **Know when to stop.** Offer to proceed when you understand enough.

---

## Question Types

### Motivation
- "What prompted this?"
- "What are you doing today that this replaces?"

### Concreteness
- "Walk me through using this"
- "Give me an example"

### Clarification
- "When you say Z, do you mean A or B?"

### Success
- "How will you know this is working?"
- "What does done look like?"

### Critical Flows (Dominion Flow)
- "Is there any payment or billing involved?"
- "How do users log in?"
- "What data can users create, edit, or delete?"
- "What happens if [critical action] fails halfway?"

### Technical Risks (Dominion Flow)
- "Have you tried building this before? What went wrong?"
- "Any third-party services this depends on?"
- "Is there existing code or data we need to work with?"

### Deployment Context (Dominion Flow)
- "Where does this need to be deployed?"
- "Any existing infrastructure?"

---

## Context Checklist

Check these mentally as you go:

### Core
- [ ] What they are building (concrete enough to explain)
- [ ] Why it needs to exist (the problem driving it)
- [ ] Who it is for
- [ ] What "done" looks like

### SDLC Awareness (Dominion Flow)
- [ ] Critical flows identified (payment, auth, data mutation)
- [ ] Known technical risks surfaced
- [ ] Third-party dependencies listed
- [ ] Deployment target understood
- [ ] Data sensitivity level (PII, financial, public)

---

## Decision Gate

When you could write a clear PROJECT.md, offer to proceed:

- header: "Ready?"
- question: "I think I understand what you are after. Ready to create PROJECT.md?"
- options: ["Create PROJECT.md", "Keep exploring"]

---

## Dominion Flow PROJECT.md Additions

```markdown
## Critical Flows (Mandatory Testing)
- [ ] [Flow 1]: requires [unit/integration/e2e] tests
- [ ] [Flow 2]: requires [unit/integration/e2e] tests

## Known Risks
| Risk | Severity | Mitigation |
|------|----------|------------|
| [Risk 1] | High | [Plan] |

## Third-Party Dependencies
| Service | Purpose | Fallback |
|---------|---------|----------|
| [Service] | [Why] | [If unavailable] |
```

---

## Anti-Patterns

- Checklist walking (going through domains regardless of context)
- Corporate speak ("Who are your stakeholders?" for solo project)
- Interrogation (firing questions without building on answers)
- Shallow acceptance (taking vague answers without probing)
- Skipping critical flows (not asking about payment/auth/mutations)
- Asking about user's technical experience (Claude builds, not the user)
