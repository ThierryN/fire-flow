# Campaign Analytics & Attribution

## Triggers
Use when: campaign performance, attribution modeling, funnel analysis, ROI calculation, ROAS, CAC, conversion funnel, marketing analytics

---

## Attribution Models

| Model | Description | Best For |
|-------|-------------|---------|
| First-touch | 100% credit to first interaction | Brand awareness campaigns |
| Last-touch | 100% credit to last interaction | Direct response |
| Linear | Equal credit across all touchpoints | Long consideration cycles |
| Time-decay | More credit to recent touchpoints | Short sales cycles |
| Position-based (W-shaped) | 40% first, 40% last, 20% middle | Balanced view |

**W-Shaped (recommended default):**
- 40% credit → First touch (awareness)
- 20% credit → Middle touches (nurture)
- 40% credit → Last touch (conversion)

---

## Funnel Analysis

**Stage definitions:**
```
Awareness → Interest → Consideration → Intent → Purchase → Retention
```

**Conversion rate benchmarks (B2B SaaS):**
| Stage | Conversion Rate |
|-------|----------------|
| Visit → Lead | 2–5% |
| Lead → MQL | 25–40% |
| MQL → SQL | 15–30% |
| SQL → Opportunity | 40–60% |
| Opportunity → Close | 20–30% |

**Bottleneck detection:**
- Find the stage with the biggest drop-off
- That's your highest-leverage optimization point
- If Visit→Lead is low: fix landing page / CTA
- If MQL→SQL is low: fix lead scoring or SDR process
- If SQL→Close is low: fix sales enablement or pricing

---

## ROI Metrics

```
ROI  = (Revenue - Cost) / Cost × 100
ROAS = Revenue / Ad Spend
CPA  = Total Spend / Conversions
CPL  = Total Spend / Leads
CAC  = Total Sales & Marketing Spend / New Customers
```

**Industry benchmarks:**
| Metric | B2B SaaS Target |
|--------|----------------|
| ROAS | >3:1 |
| CAC Payback | <12 months |
| LTV:CAC | >3:1 |
| Blended CAC | <$300 (SMB) |
| MQL→SQL rate | >15% |

---

## Campaign Reporting Template

```markdown
## Campaign: [Name]
**Period:** [Start] – [End]
**Budget:** $[X]  |  **Spent:** $[Y]

### Performance
| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Impressions | | | |
| Clicks | | | |
| CTR | | | |
| Conversions | | | |
| CPA | | | |
| ROI | | | |

### Attribution
- First-touch source: [Channel]
- Highest-volume middle touch: [Channel]
- Last-touch source: [Channel]

### Key Findings
1. [What worked]
2. [What didn't]
3. [Recommended action]
```
