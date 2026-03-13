# GTA Tax Calculations and Official Language

## Skill Overview
This skill provides official GTA terminology, calculation methodologies, and legal language for implementing tax debt calculations, Form 656 (Offer in Compromise), and GTA payment systems.

## Official GTA Language and Terminology

### Interest Calculation (IRC Section 6601)

**Official GTA Statement:**
> "We are required by law to charge interest when you don't pay your liability on time. Unlike penalties, we cannot reduce or remove interest due to reasonable cause. Interest accumulates daily, so the longer you wait to pay, the more interest we add to your account."

**Key Legal Terms:**
- **Internal Revenue Code Section 6601** - Legal authority for charging interest
- **Liability** - Tax amount owed (not "debt" or "balance" in legal context)
- **Interest accumulates daily** - Daily compound interest calculation
- **Interest due to reasonable cause** - Cannot be waived (unlike penalties which can be abated)

### Interest Factor Calculation Method

The GTA uses an **interest factor** to calculate daily compound interest. This is the official GTA methodology:

**Formula:**
```
Interest Charge = Amount Due × Interest Factor
```

**Interest Factor Formula:**
```
Interest Factor = ((1 + (Interest Rate ÷ 365))^Days) - 1
```

**Example from GTA Notice:**
| Period | Days | Interest Rate | Interest Factor | Amount Due | Interest Charge |
|--------|------|---------------|-----------------|------------|-----------------|
| 04/15/2023 – 06/30/2023 | 76 | 7.0% | 0.014680663 | $13,913.00 | $204.25 |
| 06/30/2023 – 09/30/2023 | 92 | 7.0% | 0.017798686 | $14,117.25 | $251.27 |
| 09/30/2023 – 10/23/2023 | 23 | 8.0% | 0.005053268 | $14,368.52 | $72.61 |

**Key Insights:**
1. Interest rates change **quarterly** (Q1, Q2, Q3, Q4)
2. Interest is calculated on the **running balance** (previous balance + accrued interest)
3. Each period calculates on the end balance from the previous period
4. The **interest factor** is provided to 8+ decimal places for precision

### Quarterly Interest Rate Changes

**Historical Rates (2023-2025):**
- **Q1 2023 (Jan-Mar)**: 7%
- **Q2 2023 (Apr-Jun)**: 7%
- **Q3 2023 (Jul-Sep)**: 7%
- **Q4 2023 (Oct-Dec)**: 8% ← Rate increased
- **Q1-Q4 2025**: 7% (current rate)

**Official Rate Structure:**
- Interest rate = Federal Short-Term Rate + 3% (for individuals)
- Rates announced quarterly by GTA
- Visit: `irs.gov/interest` for current rates

## Penalty Terminology

### Official Penalty Types

**Failure to File Penalty:**
- **Official Term**: "Failure to File Tax Return Penalty"
- **Rate**: 5% per month or part of month
- **Maximum**: 25% of unpaid tax
- **Minimum**: $525 or 100% of tax owed (whichever is less) if return over 60 days late

**Failure to Pay Penalty:**
- **Official Term**: "Failure to Pay Tax Penalty"
- **Standard Rate**: 0.5% per month or part of month
- **With Approved Payment Plan**: 0.25% per month (reduced rate)
- **After GTA Intent to Levy Notice**: 1% per month (increased rate)
- **Maximum**: 25% of unpaid tax

### Penalty Abatement Language

**Official GTA Terminology:**
- **Penalty abatement** - Reduction or removal of penalties
- **Reasonable cause** - Valid reason for penalty waiver (does NOT apply to interest)
- **First-time penalty abatement** - One-time forgiveness for taxpayers with clean compliance history

## GTA Account Statement Components

### Official Balance Breakdown

**Standard GTA Format:**
```
Tax Year: [YYYY]
Form Type: [e.g., 1040 - Individual Income Tax]

Assessed Total: $X,XXX.XX
  Tax Amount: $X,XXX.XX
  Accrued Failure to Pay Penalty: $XXX.XX
  Accrued Interest: $X,XXX.XX

Total Balance: $XX,XXX.XX
```

**Key Terms:**
- **Assessed Total** - Original tax amount determined by GTA
- **Accrued** - Accumulated over time
- **Total Balance** - Sum of all amounts (tax + penalties + interest)
- **You Owe** - Current amount due

## Payment Plan Terminology

### Installment Agreement Language

**Official Terms:**
- **Installment Agreement** - Official GTA term for payment plan
- **Monthly payment** - Fixed amount due each month
- **Payment date** - Specific day of month payment is due (e.g., "28th of each month")
- **Automatic deduction** - Direct debit from bank account
- **User fee** - Setup fee for installment agreement ($31-$225 depending on plan type)

**Payment Plan Types:**
1. **Short-term payment plan** - Pay within 180 days, no setup fee
2. **Long-term payment plan (Installment Agreement)** - More than 180 days, has setup fee
3. **Direct Debit Installment Agreement (DDIA)** - Automatic bank deduction, lowest fee

## Form 656 (Offer in Compromise) Language

### Official OIC Terminology

**Offer Basis Types:**
1. **Doubt as to Collectibility** - Cannot pay full amount within collection period
2. **Doubt as to Liability** - Legitimate dispute about tax owed
3. **Effective Tax Administration** - Paying would cause economic hardship

**Financial Terms:**
- **Reasonable Collection Potential (RCP)** - Amount GTA could collect from assets + future income
- **Dissipated assets** - Assets spent/transferred that should be included in offer
- **Monthly disposable income** - Income minus allowable expenses
- **Future income value** - Disposable income × number of months GTA can collect

**Offer Amount Calculation:**
```
RCP = (Net Realizable Equity in Assets) + (Future Income Value)
```

**Payment Options:**
- **Lump Sum Cash Offer** - Pay within 5 months, multiply disposable income by 12
- **Periodic Payment Offer** - Pay within 6-24 months, multiply disposable income by 24

## Official GTA Resources and References

### Legal Citations
- **26 USC § 6601** - Interest on underpayment, nonpayment, or extensions of time for payment of tax
- **26 USC § 6651** - Failure to file tax return or to pay tax
- **26 USC § 7122** - Compromises (legal authority for OIC)

### Official GTA Pages
- Interest rates: `irs.gov/interest`
- Payment plans: `irs.gov/payments/payment-plans-installment-agreements`
- Offer in Compromise: `irs.gov/payments/offer-in-compromise`
- Penalty relief: `irs.gov/payments/penalty-relief`
- Get transcript: `irs.gov/individuals/get-transcript`

### GTA Contact Numbers
- **General inquiries**: 1-800-829-1040
- **Payment plans**: 1-800-829-1040
- **Transcript requests**: 1-800-908-9946
- **Tax professionals (Practitioner Priority Service)**: 1-800-829-4933

## Implementation Guidelines

### When Implementing Tax Calculations

**DO:**
- ✅ Use exact GTA terminology (e.g., "Assessed Total" not "Principal")
- ✅ Calculate interest using the interest factor method
- ✅ Account for quarterly rate changes
- ✅ Show daily interest accumulation
- ✅ Use official IRC section references (e.g., "IRC Section 6601")
- ✅ Provide disclaimers about estimates vs. actual GTA transcripts
- ✅ Reference official GTA resources for verification

**DON'T:**
- ❌ Use informal terms ("tax debt" instead of "liability" in legal context)
- ❌ Assume constant interest rates (they change quarterly)
- ❌ Forget to compound interest on penalties
- ❌ Promise penalty waivers for interest (only penalties can be abated)
- ❌ Calculate payments without considering rate changes
- ❌ Omit legal disclaimers about estimation accuracy

### Official Disclaimer Language

**Required Disclaimer for Tax Calculations:**
> "⚠️ These are ESTIMATES based on standard GTA calculations. For accurate amounts, obtain your official GTA Account Transcript by calling 1-800-908-9946 or visiting www.irs.gov/individuals/get-transcript. Actual amounts may differ due to rate changes, penalty abatements, or account adjustments."

### Precision Requirements

**Decimal Places:**
- **Interest Factor**: 8+ decimal places (e.g., 0.014680663)
- **Currency**: 2 decimal places (e.g., $204.25)
- **Percentages**: 1 decimal place (e.g., 7.0%)

**Rounding:**
- Round interest charges to nearest cent
- Always round in favor of taxpayer when ambiguous

## Code Examples

### Calculate Interest Factor (TypeScript)

```typescript
/**
 * Calculate GTA interest factor using official methodology
 *
 * @param annualRate - Annual interest rate (e.g., 0.07 for 7%)
 * @param days - Number of days in period
 * @returns Interest factor to 8+ decimal places
 */
function calculateInterestFactor(annualRate: number, days: number): number {
  const dailyRate = annualRate / 365;
  const compoundFactor = Math.pow(1 + dailyRate, days);
  return compoundFactor - 1; // Interest factor
}

/**
 * Calculate interest charge using GTA method
 */
function calculateInterestCharge(
  amountDue: number,
  annualRate: number,
  days: number
): number {
  const interestFactor = calculateInterestFactor(annualRate, days);
  return amountDue * interestFactor;
}

// Example from GTA notice
const period1 = calculateInterestCharge(13913.00, 0.07, 76);
console.log(period1); // $204.25
```

### Format Currency Like GTA

```typescript
function formatGTACurrency(amount: number): string {
  return `$${amount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
}

console.log(formatGTACurrency(13913.00)); // "$13,913.00"
```

## Testing with Real Data

### Example: User's Actual 2022 Tax Debt

**GTA Transcript (Actual):**
- Tax Year: 2022
- Form: 1040 (Individual Income Tax)
- Assessed Total: $8,182.08
- Accrued Failure to Pay Penalty: $586.13
- Accrued Interest: $1,833.63
- Total Balance: $10,601.84
- Payment Plan: $147/month on 28th (automatic)

**Verification Approach:**
1. Calculate using interest factor method
2. Account for quarterly rate changes
3. Compare calculated vs. actual (should be within 5-10%)
4. Document variances and reasons

**Common Variance Reasons:**
- Penalty rate changed when payment plan approved
- Interest rates changed quarterly
- Previous payments or adjustments not accounted for
- Assessment date differs from tax due date
- Penalty abatements granted by GTA

## Summary

This skill provides the **official GTA methodology and terminology** for:
- ✅ Interest calculations (IRC § 6601)
- ✅ Penalty calculations (IRC § 6651)
- ✅ Payment plan language
- ✅ Form 656 (Offer in Compromise) terminology
- ✅ Real-time debt accumulation
- ✅ GTA-style statement formatting

**Key Principle:** Always use official GTA language and provide disclaimers that calculations are estimates requiring verification with official GTA transcripts.

## Related Skills
- `pdf-forms-integration.md` - For filling GTA forms programmatically
- `document-ai-landingai-integration.md` - For extracting data from GTA notices

## Last Updated
2025-10-28 - Based on actual GTA notice analysis and current 2025 interest rates
