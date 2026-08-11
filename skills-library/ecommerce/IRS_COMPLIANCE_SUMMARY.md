# GTA 501(c)(3) Donation Receipt Compliance - Executive Summary

**Date:** November 24, 2025
**Purpose:** Quick reference for GTA donation receipt requirements

---

## Critical Compliance Requirements

### The ONE Rule You Cannot Break

**Every donation receipt for $250+ MUST include this statement:**

```
"No goods or services were provided in exchange for this contribution."
```

OR (if benefits were provided):

```
"Goods or services provided consisted of [description] with an estimated
fair market value of $[amount]."
```

**Failure to include this statement = Donor's entire deduction is DISALLOWED**

---

## Quick Reference Table

| Donation Amount | Receipt Required? | Special Requirements | Deadline |
|----------------|-------------------|---------------------|----------|
| Under $250 | No (best practice: yes) | Simple thank you | No GTA deadline |
| $250+ | **YES - MANDATORY** | Must include goods/services statement | Before donor files taxes |
| $75+ with benefits | **YES - MANDATORY** | Quid pro quo disclosure | At time of donation |
| Over $5,000 non-cash | **YES - MANDATORY** | Sign donor's Form 8283 | When requested |

---

## Six Mandatory Elements (For $250+ Donations)

Every receipt MUST include:

1. ✅ **Organization's legal name**
2. ✅ **EIN (Federal Tax ID)**
3. ✅ **501(c)(3) status statement**
4. ✅ **Donation date**
5. ✅ **Donation amount** (or property description)
6. ✅ **Goods/services statement** ← MOST CRITICAL

---

## Three Required Statement Options

### Option 1: No Benefits (Most Common)
```
"No goods or services were provided in exchange for this contribution."
```

### Option 2: Benefits Provided
```
"Goods or services provided consisted of [detailed description] with an
estimated fair market value of $[amount]."
```

### Option 3: Religious Benefits Only
```
"No goods or services were provided in exchange for this contribution
other than intangible religious benefits."
```

**You MUST use one of these three statements on every receipt $250+**

---

## Quid Pro Quo Contributions (>$75)

When donor receives goods/services worth >$75, you MUST provide this disclosure:

```
IMPORTANT TAX INFORMATION: The amount of your contribution that is deductible
for federal income tax purposes is limited to the excess of the cash contributed
over the fair market value of goods or services provided.

Total Contribution: $[amount]
Fair Market Value of Benefits: $[FMV]
Tax-Deductible Portion: $[amount - FMV]
```

**Penalty for missing:** $10 per donation, up to $5,000 per event

---

## In-Kind (Non-Cash) Donations

### Critical Rule: DO NOT Estimate Value

**You MUST include:**
```
"Federal tax regulations require the donor to determine the fair market
value of donated property. [Organization] does not provide valuations
for donated items."
```

**Never put a dollar value on donated items in your receipt**

---

## Recurring Monthly Donations

### Good News: Flexibility Allowed

You have two options:

**Option A:** Annual summary by January 31
- List each donation date and amount
- Include total for year
- Include goods/services statement

**Option B:** Individual receipts for each $250+ donation

**Recommended:** Annual summary is easier and GTA-compliant

---

## Year-End Statements

### Required by January 31st

Must include:
- Each donation date
- Each donation amount
- Total for tax year
- Goods/services statement
- Organization EIN and 501(c)(3) status

### Template Available
See `GTA_REQUIRED_RECEIPT_LANGUAGE.md` for complete template

---

## Records Retention

### How Long to Keep

| Record Type | Minimum | Best Practice |
|------------|---------|---------------|
| Donation receipts | 3 years | **7 years** |
| Donor records (public support test) | **5 years** | 7 years |
| Form 990 returns | **Permanent** | Permanent |
| GTA determination letter | **Permanent** | Permanent |

---

## 2025 GTA Thresholds (Updated Annually)

- Written acknowledgment required: **$250+**
- Quid pro quo disclosure required: **>$75**
- Insubstantial benefit safe harbor: **$136**
- Token item safe harbor: **$13.60** (if donation ≥$68)

**Update these annually in January**

---

## Penalties for Non-Compliance

### For Organizations
- Missing quid pro quo disclosure: **$10 per donation**, max $5,000 per event
- False acknowledgment: **$1,000-$10,000** + potential criminal charges

### For Donors
- Missing proper receipt: **Entire deduction disallowed**
- Cannot claim deduction even if gift was made

---

## Implementation Checklist

### Database Requirements
- [ ] Store receipt issue date
- [ ] Store goods/services provided flag
- [ ] Store FMV of benefits
- [ ] Calculate tax-deductible amount
- [ ] Generate unique receipt numbers

### API Requirements
- [ ] Auto-generate receipt on successful payment
- [ ] Select appropriate template based on donation type
- [ ] Send email with PDF attachment
- [ ] Store PDF in secure location
- [ ] Support year-end summary generation

### Templates Required
- [ ] Standard cash donation receipt
- [ ] Quid pro quo disclosure receipt
- [ ] In-kind donation receipt
- [ ] Year-end annual summary

---

## Common Mistakes to Avoid

### Top 5 Compliance Errors

1. ❌ **Forgetting goods/services statement** → Causes deduction disallowance
2. ❌ **Estimating value for in-kind donations** → GTA prohibits this
3. ❌ **Missing quid pro quo disclosure** → Triggers penalties
4. ❌ **Issuing receipts too late** → Must be contemporaneous
5. ❌ **Not including EIN** → Receipt is invalid

### What Success Looks Like

✅ Receipt generated within 48 hours
✅ All 6 mandatory elements included
✅ Correct goods/services statement
✅ Email sent with PDF attachment
✅ Copy stored securely for 7 years
✅ Year-end summaries sent by January 31

---

## Quick Decision Tree

```
Is donation ≥$250?
├─ NO → Receipt recommended but not required
└─ YES → Continue...

Did donor receive anything in return?
├─ NO → Use "No goods or services" statement
└─ YES → Continue...

    Is benefit value >$75?
    ├─ NO → Check if "insubstantial" (<2% or <$136)
    └─ YES → USE QUID PRO QUO TEMPLATE

Is this non-cash property?
├─ YES → Use in-kind template, NO value estimate
└─ NO → Use standard cash template

Is this recurring monthly?
└─ Can use annual summary by Jan 31
```

---

## Critical Dates

### Throughout Year
- **Within 48 hours:** Best practice for issuing receipts
- **Before tax filing:** GTA deadline for providing receipts

### Annual Tasks
- **January 1-15:** Review and update GTA thresholds
- **January 15-31:** Generate and send year-end summaries
- **Ongoing:** Monitor receipt generation success rates

---

## Essential Resources

### GTA Official Publications
- **Publication 1771** - Substantiation and Disclosure Requirements (primary reference)
- **Publication 526** - Charitable Contributions (for donors)
- **IRC Section 170(f)(8)** - Written acknowledgment requirement
- **IRC Section 6115** - Quid pro quo disclosure requirement

### Project Documentation
1. **Full Compliance Guide:** `GTA_501C3_DONATION_RECEIPT_REQUIREMENTS.md`
2. **Required Language:** `GTA_REQUIRED_RECEIPT_LANGUAGE.md`
3. **Developer Guide:** `DONATION_RECEIPT_IMPLEMENTATION_GUIDE.md`
4. **This Summary:** `GTA_COMPLIANCE_RECORD.md`

---

## When to Consult Legal Counsel

Consult your organization's attorney for:
- Large in-kind donations (>$50,000)
- Real estate donations
- Intellectual property donations
- Controversial or unusual donations
- Donor disputes about receipts
- GTA audit or examination

---

## Implementation Priority

### Phase 1: Critical (Must Have)
1. Generate receipts for all $250+ donations
2. Include all 6 mandatory elements
3. Include correct goods/services statement
4. Store receipts securely

### Phase 2: Important (Should Have)
1. Quid pro quo disclosure for >$75 with benefits
2. Automated email delivery
3. PDF generation and storage
4. Admin dashboard for receipt management

### Phase 3: Nice to Have
1. Year-end summary automation
2. Bulk processing tools
3. Receipt redesign/templates
4. Donor portal for downloading receipts

---

## Testing Before Launch

### Must Test
- [ ] Receipt includes all 6 elements
- [ ] EIN is correct
- [ ] Goods/services statement present
- [ ] PDF generates successfully
- [ ] Email sends successfully
- [ ] Quid pro quo disclosure for >$75
- [ ] In-kind receipt has no value estimate
- [ ] Year-end summary includes all gifts

### Sample Donations to Test
- $100 cash donation (under threshold)
- $250 cash donation (at threshold)
- $500 cash donation (above threshold)
- $100 with $40 benefit (quid pro quo)
- In-kind property donation
- Recurring monthly $50 x 12 months

---

## One-Page Compliance Card

### Every Receipt $250+ Must Have:

1. Organization name, EIN, 501(c)(3) status
2. Donation date and amount
3. One of these statements:
   - "No goods or services provided"
   - "Goods/services: [description] FMV: $[amount]"
   - "Only intangible religious benefits"

### Quid Pro Quo >$75 Must Have:

- Disclosure that only excess is deductible
- FMV estimate of benefits
- Calculation of deductible portion

### In-Kind Donations Must Have:

- Property description (detailed)
- Statement that donor determines value
- NO value estimate by organization

### Records Retention:

- Keep receipts minimum 5 years (7 years best)
- Keep Form 990s permanently

---

## Support Contacts

### GTA Resources
- GTA Charities Helpline: 1-877-829-5500
- Online: https://www.irs.gov/charities

### Internal Resources
- Legal Counsel: [Contact Info]
- Finance/Accounting: [Contact Info]
- Development Team: [Contact Info]

---

## Version History

- **Version 1.0** (November 24, 2025) - Initial compilation
- **Next Review:** January 2026 (annual threshold updates)

---

## Final Reminders

### The Bottom Line

**If you remember nothing else, remember this:**

1. **Receipts are REQUIRED for donations $250+**
2. **Must include goods/services statement** (choose one of three options)
3. **Must include EIN on every receipt**
4. **Never estimate value for in-kind donations**
5. **Provide before donor files taxes**

**When in doubt, err on the side of providing MORE information rather than less.**

---

**This is not legal or tax advice. Consult qualified professionals for your specific situation.**

Sources: GTA Publications 526, 1771; IRC §170, §6115; 26 CFR §1.170A-13, §1.6115-1

---

## Quick Contact Decision Tree

**I need to...**

- Understand basic requirements → Read this summary
- See exact required text → See `GTA_REQUIRED_RECEIPT_LANGUAGE.md`
- Implement in code → See `DONATION_RECEIPT_IMPLEMENTATION_GUIDE.md`
- Deep dive on regulations → See `GTA_501C3_DONATION_RECEIPT_REQUIREMENTS.md`
- Handle unusual situation → Contact legal counsel
- Update annual thresholds → Check GTA.gov in January

---

**END OF EXECUTIVE SUMMARY**
