---
name: oss-daily-growth-intelligence
category: growth-marketing
version: 1.0.0
contributed: 2026-03-10
contributor: fire-flow
last_updated: 2026-03-10
tags: [github, npm, analytics, marketing, growth, open-source, social-media, psyops]
difficulty: medium
scope: general
---

# OSS Daily Growth Intelligence

## Problem

After launching an open-source project you need to:
1. Track daily traction without manually hitting GitHub/npm every morning
2. Maintain a visual report that you can screenshot and share
3. Systematically boost exposure beyond the initial launch spike

Manual checking is inconsistent. Post-launch traffic decays fast. Most OSS projects die after the first viral day because the author stops pushing. This skill captures the full daily intelligence + marketing loop.

## Solution Pattern

### Part 1 — Daily Metrics Pull (7AM loop)

Run every morning at 7AM via `/loop 24h`:

```bash
# GitHub traffic (views + clones)
gh api repos/{OWNER}/{REPO}/traffic/views
gh api repos/{OWNER}/{REPO}/traffic/clones
gh api repos/{OWNER}/{REPO}/traffic/popular/referrers
gh api repos/{OWNER}/{REPO}/traffic/popular/paths

# Repo stats
gh api repos/{OWNER}/{REPO} --jq '{stars:.stargazers_count,forks:.forks_count}'

# npm daily downloads
curl -s "https://api.npmjs.org/downloads/range/{DATE_RANGE}/{PACKAGE}"
```

Update `~/.claude/mission-control/fire-flow-traffic.json` with new data.
Update `Documents/Claude Reports/fire-flow-traffic-report.html` (full dashboard).
Update `Documents/Claude Reports/fire-flow-launch-card.html` (Facebook post card).

Summarize changes vs yesterday:
- Stars delta, forks delta
- Views delta, new top referrers
- npm installs delta
- Flag any anomalies (traffic spike = someone shared it)

### Part 2 — Insight Output

Each morning's loop should produce:

```
fire-flow Daily Pulse — {DATE}
────────────────────────────
Stars:    {N} (+{delta})
Forks:    {N} (+{delta})
Views:    {N} (+{delta})  ← {top referrer today}
npm:      {N} (+{delta})
────────────────────────────
Alert: {any spike or trend note}
Marketing suggestion: {one action from the radical tactics list}
```

## Loop Setup Command

Start at 7AM daily (run this command AT 7AM so the 24h cycle aligns):

```
/loop 24h Pull GitHub and npm traffic for ThierryN/fire-flow using gh CLI and npm registry API. Update C:\Users\Thierry\Documents\Claude Reports\fire-flow-traffic.json with new daily data. Compare to previous day. Update both HTML report files. Output the daily pulse summary with marketing suggestion.
```

## C3 Integration

Add to `~/.claude/mission-control/reminders.json`:
- Daily 7AM reminder to start the loop if not already running
- Weekly Sunday reminder to post the traffic card on Facebook

---

## Part 3 — Radical Marketing Tactics (OSS Psyops)

These are proven psychological triggers for OSS growth. Apply one per day.

---

### Tier 1: High-Leverage Posts (do first)

**1. Transparent Metrics Post**
Post the fire-flow-launch-card.html screenshot directly to every AI/Claude Facebook group.
Caption: "Day {N}: fire-flow — {stars} stars, {downloads} downloads, {views} GitHub views in {N} days. Free plugin for Claude Code."
Why it works: Real numbers trigger FOMO and credibility simultaneously. Most devs never share metrics. The transparency is disarming.

**2. The Before/After Story**
"I vibe-coded a 60,000 line app over 6 months. fire-flow helped me rebuild it clean — 19,986 lines, full TypeScript, 137 tests — in one autonomous session."
Why it works: Specific numbers + personal story = highest-engagement post format. This is the Scribal Priest rebuild story. USE IT.

**3. The Live Challenge**
"Drop your hardest build task below. I'll run fire-flow on it and post the result."
Why it works: Engagement bait + live demo + social proof. Every comment = algorithm fuel.

**4. The Contrast Hook**
"Everyone is using Claude Code. Almost nobody knows there's a free planning + execution layer that eliminates token waste and random hallucinations."
Why it works: In-group identity + exclusivity + implies the reader is about to get an unfair advantage.

---

### Tier 2: Discovery Channels (sustained traffic)

**5. Product Hunt Launch**
- Schedule for Tuesday or Wednesday at 00:01 PT
- Pre-build hunter list (DM 20 people who upvote AI tools)
- Tagline: "The missing planning layer for Claude Code — 511+ battle-tested skills"
- First comment: the before/after story

**6. Show HN (Hacker News)**
Title: "Show HN: fire-flow – orchestration system for Claude Code (66% codebase reduction)"
Body: Lead with the Scribal Priest rebuild numbers. Link to GitHub.
Best time: Monday/Tuesday 9AM ET

**7. Reddit Posts**
- r/ClaudeAI — "I built a planning/execution plugin for Claude Code. 36 stars in 8 days."
- r/LocalLLaMA — Focus on token efficiency angle
- r/programming — Focus on the autonomous rebuild story
- r/SideProject — "Built this for myself, 925 people downloaded it in 8 days"

**8. Awesome Lists Submission**
Submit to:
- awesome-claude-code (GitHub)
- awesome-ai-agents
- awesome-llm-tools
- awesome-chatgpt-prompts (stretch)
These drive sustained long-tail organic installs for months.

---

### Tier 3: Parasitic Growth (amplify existing audiences)

**9. Reply Seeding**
Find viral posts about Claude Code from @swyx, @karpathy, Claude official (@AnthropicAI), and any AI tool posts with 100+ likes. Reply with:
"This is where fire-flow helps — [specific relevant use case]. Free plugin: github.com/ThierryN/fire-flow"
Why it works: You get the eyeballs of an already-engaged audience with zero spend.

**10. Micro-Influencer DMs (10 people)**
Find developers with 5k–50k followers who post about AI coding tools.
Message: "Hey {name}, I built a free orchestration plugin for Claude Code. {specific reason it's relevant to their content}. Want me to send you a private demo?"
10 DMs → 2-3 responses → 1-2 posts = 500+ new installs.

**11. YouTube Short (60 seconds)**
Screen record: Open terminal → `npx @thierrynakoa/fire-flow` → pick a project → watch fire-flow plan and execute a feature autonomously.
No voiceover needed. Add captions. Post to YouTube Shorts, TikTok, Instagram Reels.
Why it works: Video of code running autonomously is hypnotic. Gets shared without prompting.

---

### Tier 4: Content Momentum (algorithm food)

**12. The Build Diary (daily serial)**
Post every day: "Day {N} of fire-flow:"
Keep it to 2–3 lines + one screenshot.
Day 8: 36 stars. Day 9: 38 stars. Small wins compound.
Serial content trains the algorithm to push your account.

**13. Dev.to / Hashnode / Medium Article**
Title: "How fire-flow cut my Claude Code sessions from 3 hours to 45 minutes"
This ranks on Google for "Claude Code plugin", "Claude Code orchestration" etc.
One article = 6 months of passive discovery traffic.

**14. Controversial Take (engagement bait)**
"Hot take: Using Claude Code without a planning layer is like deploying to prod without tests. You'll get there, but not the way you wanted."
Replies = reach. Even disagreement = algorithm boost.

**15. The "0 to 925" Story**
"8 days ago I pushed a GitHub repo. Here's exactly what happened:"
Then tell the story: no marketing budget, just sharing in Facebook groups, 65% of traffic from FB, 373 npm installs, viral day = 558 views.
Meta-content about building in public performs extremely well.

---

## When to Use Each Tactic

| Tactic | When | Expected Result |
|--------|------|----------------|
| Transparent Metrics Post | Daily (morning) | 50–200 views/post |
| Before/After Story | Once now, repurpose | Highest engagement, shareable |
| Live Challenge | When engagement slows | 20–50 comments |
| Product Hunt | Week 2–3 | 100–500 new stars/installs |
| Show HN | Any weekday morning | 200–2000 views if it hits front page |
| Reddit posts | 1 per community | 50–500 visits per post |
| Awesome Lists | One-time, this week | Steady 10–30 installs/week long-term |
| Reply Seeding | Daily (5 min) | Compound visibility over weeks |
| Micro-influencer DMs | 10 this week | 1–3 posts from real users |
| YouTube Short | ASAP | 500–5000 views within 2 weeks |
| Build Diary | Daily | Algorithm momentum |

---

## Anti-Patterns (What NOT to Do)

- **Do NOT spam** the same post in 10 groups at the same time. Stagger by 2–3 days.
- **Do NOT lead with features** — lead with outcomes and stories. Nobody shares "I added X feature."
- **Do NOT ignore replies** — respond to every comment in the first hour. Algorithm gold.
- **Do NOT post only when you have something new** — consistency > novelty for discovery.
- **Do NOT skip the daily metrics pull** — you can't market intelligently without knowing what's moving.

---

## Related Skills

- `fire-flow-traffic-report` — HTML dashboard template
- `github-api-patterns` — gh CLI reference
- `social-media-post-card` — Facebook post image generation

## References

- GitHub Traffic API: https://docs.github.com/en/rest/metrics/traffic
- npm Downloads API: https://api.npmjs.org/downloads/range/{period}/{package}
- fire-flow repo: github.com/ThierryN/fire-flow
- Reports: `C:\Users\Thierry\Documents\Claude Reports\`
