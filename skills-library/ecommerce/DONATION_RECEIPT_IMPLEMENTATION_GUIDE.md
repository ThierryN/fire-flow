# Donation Receipt Implementation Guide for Developers

## Purpose
This guide helps developers implement GTA-compliant donation receipt generation in the MERN Community LMS application.

---

## Overview

### What We're Building
An automated system that generates GTA-compliant 501(c)(3) donation receipts based on:
- Donation amount thresholds
- Whether goods/services were provided in return
- Type of donation (cash vs. in-kind)
- Frequency (one-time vs. recurring)

---

## Database Schema Requirements

### Required Fields in Donation/Transaction Table

```javascript
{
  // Existing fields
  donationId: String,
  userId: ObjectId,
  amount: Number,
  donationType: String, // 'one-time' | 'recurring' | 'in-kind'
  status: String,
  createdAt: Date,

  // NEW REQUIRED FIELDS FOR GTA COMPLIANCE

  // Receipt Information
  receiptIssued: Boolean,
  receiptIssuedAt: Date,
  receiptNumber: String, // Unique receipt identifier

  // Quid Pro Quo Information
  goodsServicesProvided: Boolean, // true if donor received anything
  goodsServicesDescription: String, // Description of what was provided
  goodsServicesFMV: Number, // Fair Market Value of benefits
  taxDeductibleAmount: Number, // Calculated: amount - goodsServicesFMV

  // In-Kind Donations
  propertyDescription: String, // For non-cash donations
  propertyCondition: String, // As stated by donor
  donorEstimatedValue: Number, // Donor's estimate (not org's)

  // Receipt Delivery
  receiptEmailSent: Boolean,
  receiptEmailSentAt: Date,
  receiptPdfUrl: String, // S3/storage URL

  // Compliance Tracking
  requiresForm8283: Boolean, // >$5,000 non-cash
  form8283Signed: Boolean,
  form8283SignedAt: Date,
  form8283SignedBy: String // Staff member who signed
}
```

### Organization Configuration Fields

```javascript
// In organization/settings collection
{
  organizationLegalName: String,
  ein: String, // Federal Tax ID
  taxExemptStatus: String, // Should be '501(c)(3)'
  address: {
    street: String,
    city: String,
    state: String,
    zipCode: String
  },
  receiptSettings: {
    autoSendReceipts: Boolean,
    receiptEmailFrom: String,
    receiptSignatureName: String,
    receiptSignatureTitle: String,
    logoUrl: String,

    // Quid Pro Quo Defaults
    defaultEventDinnerFMV: Number, // e.g., 40 for typical meal

    // Insubstantial benefit thresholds (updated annually)
    currentYearThresholds: {
      year: 2025,
      quiddProQuoDisclosureThreshold: 75,
      writtenAcknowledgmentThreshold: 250,
      insubstantialBenefitAmount: 136,
      tokenItemAmount: 13.60,
      tokenItemMinDonation: 68
    }
  }
}
```

---

## Business Logic Rules

### Rule 1: When to Generate Receipt

```javascript
/**
 * Determine if receipt is required by GTA
 */
function isReceiptRequired(donation) {
  // GTA requires written acknowledgment for $250+
  // Best practice: always send receipt
  return donation.amount >= 250 || donation.donationType === 'in-kind';
}

/**
 * Determine if quid pro quo disclosure is required
 */
function requiresQuidProQuoDisclosure(donation) {
  // IRC Section 6115: Required for >$75 with goods/services
  return donation.amount > 75 && donation.goodsServicesProvided === true;
}
```

### Rule 2: Calculate Tax-Deductible Amount

```javascript
/**
 * Calculate the tax-deductible portion of a contribution
 */
function calculateTaxDeductibleAmount(donation, orgSettings) {
  // If no goods/services provided, full amount is deductible
  if (!donation.goodsServicesProvided) {
    return donation.amount;
  }

  // Check if benefit is "insubstantial" per GTA rules
  const thresholds = orgSettings.receiptSettings.currentYearThresholds;
  const isInsubstantial = donation.goodsServicesFMV <= Math.min(
    donation.amount * 0.02, // 2% of donation
    thresholds.insubstantialBenefitAmount // $136 in 2025
  );

  // If insubstantial, full amount is deductible
  if (isInsubstantial) {
    return donation.amount;
  }

  // Otherwise, only excess over FMV is deductible
  return Math.max(0, donation.amount - donation.goodsServicesFMV);
}
```

### Rule 3: Select Appropriate Template

```javascript
/**
 * Determine which receipt template to use
 */
function selectReceiptTemplate(donation) {
  // In-kind donations use special template
  if (donation.donationType === 'in-kind') {
    return 'TEMPLATE_IN_KIND';
  }

  // Quid pro quo contributions (>$75 with benefits)
  if (donation.amount > 75 && donation.goodsServicesProvided) {
    return 'TEMPLATE_QUID_PRO_QUO';
  }

  // Standard cash donation
  return 'TEMPLATE_STANDARD_CASH';
}
```

### Rule 4: Goods/Services Statement Selection

```javascript
/**
 * Generate the required goods/services statement
 */
function generateGoodsServicesStatement(donation) {
  // Option 1: No goods/services provided (most common)
  if (!donation.goodsServicesProvided) {
    return "No goods or services were provided in exchange for this contribution.";
  }

  // Option 2: Intangible religious benefits only
  if (donation.goodsServicesDescription === 'intangible_religious_benefits') {
    return "No goods or services were provided in exchange for this contribution other than intangible religious benefits.";
  }

  // Option 3: Goods/services were provided with FMV
  return `Goods or services that ${orgSettings.organizationLegalName} provided in exchange for your contribution consisted of ${donation.goodsServicesDescription} with an estimated fair market value of $${donation.goodsServicesFMV.toFixed(2)}.`;
}
```

---

## API Endpoints to Implement/Update

### 1. Create Donation Endpoint

```javascript
// POST /api/donations
async function createDonation(req, res) {
  const {
    amount,
    donationType,
    paymentMethod,
    goodsServicesProvided = false,
    goodsServicesDescription = null,
    goodsServicesFMV = 0,
    // For in-kind donations
    propertyDescription = null,
    propertyCondition = null
  } = req.body;

  // Calculate tax-deductible amount
  const taxDeductibleAmount = calculateTaxDeductibleAmount({
    amount,
    goodsServicesProvided,
    goodsServicesFMV
  }, organizationSettings);

  // Create donation record
  const donation = await Donation.create({
    userId: req.user.id,
    amount,
    donationType,
    paymentMethod,
    goodsServicesProvided,
    goodsServicesDescription,
    goodsServicesFMV,
    taxDeductibleAmount,
    propertyDescription,
    propertyCondition,
    receiptNumber: generateReceiptNumber(), // Implement unique ID generator
    status: 'pending',
    receiptIssued: false
  });

  // If payment successful, generate and send receipt
  if (donation.status === 'completed') {
    await generateAndSendReceipt(donation);
  }

  return res.json({ success: true, donation });
}
```

### 2. Generate Receipt Endpoint

```javascript
// POST /api/donations/:id/receipt
async function generateReceipt(req, res) {
  const donation = await Donation.findById(req.params.id)
    .populate('userId');

  if (!donation) {
    return res.status(404).json({ error: 'Donation not found' });
  }

  // Select appropriate template
  const template = selectReceiptTemplate(donation);

  // Generate receipt data
  const receiptData = {
    organization: {
      legalName: orgSettings.organizationLegalName,
      ein: orgSettings.ein,
      address: orgSettings.address,
      taxExemptStatus: '501(c)(3)'
    },
    donor: {
      name: donation.userId.fullName,
      address: donation.userId.address
    },
    donation: {
      receiptNumber: donation.receiptNumber,
      date: donation.createdAt,
      amount: donation.amount,
      taxDeductibleAmount: donation.taxDeductibleAmount,
      paymentMethod: donation.paymentMethod,
      donationType: donation.donationType
    },
    goodsServicesStatement: generateGoodsServicesStatement(donation),
    issuedDate: new Date(),
    signatureName: orgSettings.receiptSettings.receiptSignatureName,
    signatureTitle: orgSettings.receiptSettings.receiptSignatureTitle
  };

  // Generate PDF
  const pdfBuffer = await generateReceiptPDF(template, receiptData);

  // Upload to storage
  const pdfUrl = await uploadToStorage(pdfBuffer, `receipts/${donation.receiptNumber}.pdf`);

  // Update donation record
  donation.receiptIssued = true;
  donation.receiptIssuedAt = new Date();
  donation.receiptPdfUrl = pdfUrl;
  await donation.save();

  // Send email with PDF attachment
  if (orgSettings.receiptSettings.autoSendReceipts) {
    await sendReceiptEmail(donation, receiptData, pdfBuffer);
  }

  return res.json({ success: true, receiptUrl: pdfUrl });
}
```

### 3. Generate Year-End Summary Endpoint

```javascript
// POST /api/donations/year-end-summary/:userId/:year
async function generateYearEndSummary(req, res) {
  const { userId, year } = req.params;

  // Get all donations for user in tax year
  const startDate = new Date(year, 0, 1);
  const endDate = new Date(year, 11, 31, 23, 59, 59);

  const donations = await Donation.find({
    userId,
    createdAt: { $gte: startDate, $lte: endDate },
    status: 'completed'
  }).sort({ createdAt: 1 });

  // Separate cash and in-kind
  const cashDonations = donations.filter(d => d.donationType !== 'in-kind');
  const inKindDonations = donations.filter(d => d.donationType === 'in-kind');

  const totalCash = cashDonations.reduce((sum, d) => sum + d.amount, 0);

  // Generate summary data
  const summaryData = {
    organization: {
      legalName: orgSettings.organizationLegalName,
      ein: orgSettings.ein,
      address: orgSettings.address
    },
    donor: await User.findById(userId),
    taxYear: year,
    cashDonations: cashDonations.map(d => ({
      date: d.createdAt,
      amount: d.amount,
      description: d.donationType === 'recurring' ? 'Monthly Recurring Gift' : 'One-Time Donation'
    })),
    inKindDonations: inKindDonations.map(d => ({
      date: d.createdAt,
      description: d.propertyDescription
      // Note: DO NOT include value estimate
    })),
    totalCash,
    goodsServicesStatement: determineAnnualGoodsServicesStatement(donations),
    issuedDate: new Date()
  };

  // Generate PDF
  const pdfBuffer = await generateYearEndSummaryPDF(summaryData);

  // Upload and send
  const pdfUrl = await uploadToStorage(
    pdfBuffer,
    `year-end-summaries/${year}/${userId}.pdf`
  );

  await sendYearEndSummaryEmail(summaryData, pdfBuffer);

  return res.json({ success: true, summaryUrl: pdfUrl });
}
```

### 4. Admin: Sign Form 8283 Endpoint

```javascript
// POST /api/admin/donations/:id/sign-form-8283
async function signForm8283(req, res) {
  const donation = await Donation.findById(req.params.id);

  // Verify this is in-kind donation >$5,000
  if (donation.donationType !== 'in-kind' || donation.amount <= 5000) {
    return res.status(400).json({
      error: 'Form 8283 signature only required for in-kind donations over $5,000'
    });
  }

  // Verify admin authorization
  if (!req.user.isAdmin) {
    return res.status(403).json({ error: 'Unauthorized' });
  }

  // Update record
  donation.form8283Signed = true;
  donation.form8283SignedAt = new Date();
  donation.form8283SignedBy = req.user.fullName;
  await donation.save();

  // Generate acknowledgment for donor
  await sendForm8283AcknowledgmentEmail(donation);

  return res.json({ success: true, donation });
}
```

---

## Email Templates

### Immediate Receipt Email (Auto-Send)

**Subject:** Tax Receipt for Your Donation to [Organization Name]

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; }
    .header { background: #f4f4f4; padding: 20px; text-align: center; }
    .content { padding: 20px; }
    .important { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }
  </style>
</head>
<body>
  <div class="header">
    <h2>Thank You for Your Generous Donation</h2>
  </div>

  <div class="content">
    <p>Dear {{donorName}},</p>

    <p>Thank you for your generous contribution of <strong>${{amount}}</strong> to {{organizationName}} on {{donationDate}}.</p>

    <div class="important">
      <strong>TAX RECEIPT ATTACHED</strong><br>
      Your official tax receipt for GTA purposes is attached to this email as a PDF. Please save this for your tax records.
    </div>

    <h3>Donation Details:</h3>
    <ul>
      <li><strong>Receipt Number:</strong> {{receiptNumber}}</li>
      <li><strong>Date:</strong> {{donationDate}}</li>
      <li><strong>Amount:</strong> ${{amount}}</li>
      <li><strong>Payment Method:</strong> {{paymentMethod}}</li>
      {{#if goodsServicesProvided}}
      <li><strong>Tax-Deductible Portion:</strong> ${{taxDeductibleAmount}}</li>
      {{/if}}
    </ul>

    {{#if goodsServicesProvided}}
    <div class="important">
      <strong>IMPORTANT TAX INFORMATION:</strong><br>
      In accordance with GTA regulations, the tax-deductible portion of your contribution is ${{taxDeductibleAmount}}, which is the amount contributed minus the fair market value of goods or services received (${{goodsServicesFMV}}).
    </div>
    {{else}}
    <p><strong>Tax Information:</strong> No goods or services were provided in exchange for this contribution. The full amount is tax-deductible to the extent permitted by law.</p>
    {{/if}}

    <p>{{organizationName}} is a tax-exempt organization under Section 501(c)(3) of the Internal Revenue Code. Our Federal Tax ID (EIN) is {{ein}}.</p>

    <p>If you have any questions about your donation or this receipt, please contact us at {{contactEmail}} or {{contactPhone}}.</p>

    <p>With heartfelt gratitude,<br>
    <strong>{{signatureName}}</strong><br>
    {{signatureTitle}}<br>
    {{organizationName}}</p>
  </div>
</body>
</html>
```

### Year-End Summary Email

**Subject:** Your 2025 Annual Giving Statement from [Organization Name]

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; }
    .header { background: #007bff; color: white; padding: 20px; text-align: center; }
    .content { padding: 20px; }
    .summary-box { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 20px 0; }
    .important { background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; }
  </style>
</head>
<body>
  <div class="header">
    <h2>Annual Giving Statement - Tax Year {{taxYear}}</h2>
  </div>

  <div class="content">
    <p>Dear {{donorName}},</p>

    <p>Thank you for your generous support of {{organizationName}} throughout {{taxYear}}. Your partnership has made a tremendous impact on our mission.</p>

    <div class="important">
      <strong>ANNUAL TAX STATEMENT ATTACHED</strong><br>
      Your complete annual giving statement for tax year {{taxYear}} is attached as a PDF. Please retain this with your tax records.
    </div>

    <div class="summary-box">
      <h3>{{taxYear}} Giving Summary</h3>
      <p><strong>Total Cash Contributions:</strong> ${{totalCash}}</p>
      <p><strong>Number of Gifts:</strong> {{numberOfGifts}}</p>
      {{#if recurringDonor}}
      <p><strong>Monthly Giving Status:</strong> Active Sustaining Member</p>
      {{/if}}
      {{#if hasInKindDonations}}
      <p><strong>In-Kind Donations:</strong> {{inKindCount}} item(s) donated (descriptions included in attachment)</p>
      {{/if}}
    </div>

    <h3>Important Tax Information:</h3>
    <p>{{organizationName}} is a tax-exempt charitable organization under Section 501(c)(3) of the Internal Revenue Code. Our Federal Tax ID (EIN) is {{ein}}.</p>

    <p>{{goodsServicesStatement}}</p>

    <p>This acknowledgment satisfies GTA substantiation requirements for charitable contributions. Please consult your tax advisor regarding deductibility.</p>

    <p>If you notice any discrepancies or need additional information, please contact us at {{contactEmail}} or {{contactPhone}} before filing your taxes.</p>

    <p>Your generosity throughout {{taxYear}} has been a blessing. Thank you for being part of our community!</p>

    <p>With sincere gratitude,<br>
    <strong>{{signatureName}}</strong><br>
    {{signatureTitle}}<br>
    {{organizationName}}</p>
  </div>
</body>
</html>
```

---

## Frontend Components

### Donation Form Enhancements

```jsx
// Add to donation form for event tickets, galas, etc.

function DonationForm() {
  const [amount, setAmount] = useState('');
  const [receivingBenefits, setReceivingBenefits] = useState(false);
  const [benefitDescription, setBenefitDescription] = useState('');
  const [benefitFMV, setBenefitFMV] = useState(0);

  // Calculate deductible amount in real-time
  const taxDeductibleAmount = receivingBenefits
    ? Math.max(0, amount - benefitFMV)
    : amount;

  return (
    <form>
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Donation Amount"
      />

      {/* For event tickets, auctions, etc. */}
      <label>
        <input
          type="checkbox"
          checked={receivingBenefits}
          onChange={(e) => setReceivingBenefits(e.target.checked)}
        />
        I will receive goods or services for this contribution
      </label>

      {receivingBenefits && (
        <>
          <input
            type="text"
            value={benefitDescription}
            onChange={(e) => setBenefitDescription(e.target.value)}
            placeholder="Description of benefits (e.g., event dinner, auction item)"
          />
          <input
            type="number"
            value={benefitFMV}
            onChange={(e) => setBenefitFMV(e.target.value)}
            placeholder="Fair Market Value of benefits"
          />

          <div className="tax-info">
            <p><strong>Tax-Deductible Portion:</strong> ${taxDeductibleAmount.toFixed(2)}</p>
            <p className="small">
              GTA regulations require us to inform you that only ${taxDeductibleAmount.toFixed(2)}
              of your ${amount} contribution is tax-deductible.
            </p>
          </div>
        </>
      )}

      <button type="submit">Complete Donation</button>
    </form>
  );
}
```

### Receipt Download Component

```jsx
function ReceiptDownloadButton({ donationId }) {
  const [loading, setLoading] = useState(false);

  const downloadReceipt = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/donations/${donationId}/receipt`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();

      // Open PDF in new window or download
      window.open(data.receiptUrl, '_blank');

      toast.success('Receipt generated successfully!');
    } catch (error) {
      toast.error('Failed to generate receipt');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={downloadReceipt} disabled={loading}>
      {loading ? 'Generating...' : 'Download Tax Receipt'}
    </button>
  );
}
```

### Year-End Summary Request Component

```jsx
function YearEndSummaryRequest() {
  const [year, setYear] = useState(new Date().getFullYear() - 1);
  const [loading, setLoading] = useState(false);

  const requestSummary = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/donations/year-end-summary/${userId}/${year}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const data = await response.json();

      toast.success('Your year-end summary has been generated and sent to your email!');
    } catch (error) {
      toast.error('Failed to generate year-end summary');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="year-end-summary">
      <h3>Request Year-End Tax Summary</h3>
      <p>Get a comprehensive statement of all your donations for tax filing purposes.</p>

      <select value={year} onChange={(e) => setYear(e.target.value)}>
        <option value={new Date().getFullYear() - 1}>{new Date().getFullYear() - 1}</option>
        <option value={new Date().getFullYear() - 2}>{new Date().getFullYear() - 2}</option>
        <option value={new Date().getFullYear() - 3}>{new Date().getFullYear() - 3}</option>
      </select>

      <button onClick={requestSummary} disabled={loading}>
        {loading ? 'Generating...' : `Request ${year} Tax Summary`}
      </button>

      <p className="small">
        Your summary will be emailed to you within a few minutes.
      </p>
    </div>
  );
}
```

---

## Admin Dashboard Additions

### Admin: Manage Receipts Interface

```jsx
function AdminReceiptManagement() {
  const [donations, setDonations] = useState([]);

  return (
    <div>
      <h2>Receipt Management</h2>

      <table>
        <thead>
          <tr>
            <th>Donor</th>
            <th>Amount</th>
            <th>Date</th>
            <th>Receipt Issued</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {donations.map(donation => (
            <tr key={donation.id}>
              <td>{donation.donorName}</td>
              <td>${donation.amount}</td>
              <td>{formatDate(donation.createdAt)}</td>
              <td>
                {donation.receiptIssued ? (
                  <span className="badge-success">✓ Issued</span>
                ) : (
                  <span className="badge-warning">Pending</span>
                )}
              </td>
              <td>
                {!donation.receiptIssued && (
                  <button onClick={() => generateReceipt(donation.id)}>
                    Generate Receipt
                  </button>
                )}
                {donation.receiptIssued && (
                  <a href={donation.receiptPdfUrl} target="_blank">
                    View Receipt
                  </a>
                )}
                <button onClick={() => resendReceipt(donation.id)}>
                  Resend Email
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="bulk-actions">
        <h3>Bulk Year-End Processing</h3>
        <button onClick={() => generateAllYearEndSummaries(2025)}>
          Generate All 2025 Year-End Summaries
        </button>
      </div>
    </div>
  );
}
```

---

## Scheduled Jobs / Cron Tasks

### 1. Year-End Summary Generation (January 15th)

```javascript
// Run annually on January 15th
// Automatically generate year-end summaries for all donors

const cron = require('node-cron');

// Run at 2 AM on January 15th
cron.schedule('0 2 15 1 *', async () => {
  console.log('Starting automated year-end summary generation...');

  const lastYear = new Date().getFullYear() - 1;

  // Get all users who donated last year
  const donors = await Donation.distinct('userId', {
    createdAt: {
      $gte: new Date(lastYear, 0, 1),
      $lte: new Date(lastYear, 11, 31, 23, 59, 59)
    },
    status: 'completed'
  });

  // Generate summary for each donor
  for (const donorId of donors) {
    try {
      await generateYearEndSummary(donorId, lastYear);
      console.log(`Generated year-end summary for donor ${donorId}`);
    } catch (error) {
      console.error(`Failed to generate summary for donor ${donorId}:`, error);
    }
  }

  console.log('Year-end summary generation complete!');
});
```

### 2. Receipt Reminder (Monthly)

```javascript
// Check for donations without receipts issued
// Run on 1st of each month

cron.schedule('0 3 1 * *', async () => {
  console.log('Checking for missing receipts...');

  const unreceipted = await Donation.find({
    amount: { $gte: 250 },
    status: 'completed',
    receiptIssued: false,
    createdAt: { $lt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } // >7 days old
  });

  if (unreceipted.length > 0) {
    // Send alert to admin
    await sendAdminAlert({
      subject: 'Missing Donation Receipts',
      message: `${unreceipted.length} donations over $250 do not have receipts issued.`,
      donations: unreceipted
    });
  }
});
```

---

## Testing Checklist

### Unit Tests

- [ ] `calculateTaxDeductibleAmount()` - various scenarios
- [ ] `generateGoodsServicesStatement()` - all three options
- [ ] `selectReceiptTemplate()` - correct template selection
- [ ] `isReceiptRequired()` - threshold logic
- [ ] `requiresQuidProQuoDisclosure()` - threshold logic
- [ ] Receipt number generation is unique

### Integration Tests

- [ ] Create donation → receipt auto-generated
- [ ] Quid pro quo donation → disclosure included
- [ ] In-kind donation → value not estimated by org
- [ ] Year-end summary includes all donations
- [ ] Recurring donations properly aggregated
- [ ] Email delivery successful
- [ ] PDF generation successful
- [ ] S3/storage upload successful

### Compliance Tests

- [ ] All receipts include 6 mandatory elements
- [ ] EIN appears on every receipt
- [ ] Goods/services statement present on every receipt $250+
- [ ] Quid pro quo disclosure present for >$75 with benefits
- [ ] In-kind receipts don't include value estimates
- [ ] Receipt timestamps before tax deadline

### Edge Cases to Test

- [ ] Donation of exactly $250
- [ ] Donation of exactly $75 with benefits
- [ ] Multiple donations same day
- [ ] Failed payment → no receipt issued
- [ ] Refunded donation → receipt voiding
- [ ] Anonymous donation → receipt not sent but records kept
- [ ] Recurring donation canceled mid-year

---

## Deployment Checklist

### Before Launch

1. [ ] Verify organization EIN is correct in database
2. [ ] Verify organization legal name matches GTA records
3. [ ] Set up receipt email sending (SMTP/SendGrid)
4. [ ] Configure S3/storage for PDF storage
5. [ ] Load current year GTA thresholds ($136, $75, etc.)
6. [ ] Test PDF generation on production server
7. [ ] Test email delivery on production server
8. [ ] Set up cron jobs for automated processing
9. [ ] Train staff on Form 8283 signing process
10. [ ] Create admin documentation

### Post-Launch Monitoring

1. [ ] Monitor receipt generation success rate
2. [ ] Monitor email delivery success rate
3. [ ] Check for failed PDF generations
4. [ ] Review admin alerts for missing receipts
5. [ ] Audit sample of generated receipts for compliance
6. [ ] Track donor requests for duplicate receipts

### Annual Maintenance

1. [ ] Update GTA thresholds (January each year)
2. [ ] Review and update templates for any GTA guidance changes
3. [ ] Test year-end summary generation before January
4. [ ] Verify receipt signature/title is current
5. [ ] Audit prior year receipts for compliance

---

## Security Considerations

### Data Protection

- Receipt PDFs contain sensitive donor information (PII)
- Store PDFs in private S3 buckets (not public)
- Use signed URLs with expiration for access
- Encrypt PDFs at rest
- Use HTTPS for all receipt-related endpoints

### Access Control

- Only admins can regenerate receipts
- Only admins can sign Form 8283
- Users can only access their own receipts
- Audit log for all receipt generations
- Rate limiting on receipt generation endpoints

---

## Common Pitfalls to Avoid

### ❌ DON'T Do These

1. **Don't estimate value for in-kind donations** - GTA prohibits this
2. **Don't forget goods/services statement** - Most common error
3. **Don't use vague language** - Must be specific and clear
4. **Don't delay receipt generation** - Must be contemporaneous
5. **Don't include donor's value estimate on receipt** - Only descriptions
6. **Don't forget to handle refunds** - May need to void receipts
7. **Don't expose receipt PDFs publicly** - Security risk

### ✅ DO These

1. **Do generate receipts immediately upon successful payment**
2. **Do use exact GTA-required language**
3. **Do include all 6 mandatory elements**
4. **Do keep copies of all receipts generated**
5. **Do provide clear goods/services statements**
6. **Do automate year-end summaries**
7. **Do test thoroughly before tax season**

---

## Support Resources

### For Developers

- GTA Publication 1771 (PDF): https://www.irs.gov/pub/irs-pdf/p1771.pdf
- GTA Substantiation Requirements: https://www.irs.gov/charities-non-profits/substantiation-and-disclosure-requirements
- Full documentation: `docs/GTA_501C3_DONATION_RECEIPT_REQUIREMENTS.md`
- Required language reference: `docs/GTA_REQUIRED_RECEIPT_LANGUAGE.md`

### For Questions

- Consult organization's legal counsel
- Review GTA.gov/charities resources
- Test with sample donations before production use

---

**Last Updated:** November 24, 2025
**Version:** 1.0
**Maintained By:** Development Team

**Next Review:** January 2026 (annual GTA threshold updates)
