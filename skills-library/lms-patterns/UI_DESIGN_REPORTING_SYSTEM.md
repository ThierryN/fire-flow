# UI Design Specification: Admin Reporting System

**Version:** 1.0
**Date:** January 5, 2026
**Based on:** Existing PDF report format and Excel data structure

---

## Design System

### Brand Colors (from existing PDF report)

```css
:root {
  /* Primary Colors */
  --color-primary: #B91C1C;        /* Red - from logo/headers */
  --color-primary-light: #DC2626;
  --color-primary-dark: #991B1B;

  /* Secondary Colors */
  --color-secondary: #6B7280;      /* Gray - body text */
  --color-secondary-light: #9CA3AF;
  --color-secondary-dark: #4B5563;

  /* Accent Colors (for time slots) */
  --color-morning: #F59E0B;        /* Amber - Morning Intimacy */
  --color-noon: #10B981;           /* Emerald - Noon Day */
  --color-evening: #6366F1;        /* Indigo - Evening Incense */
  --color-midnight: #8B5CF6;       /* Violet - Midnight Watch */
  --color-spanish: #EF4444;        /* Red - Spanish */

  /* Status Colors */
  --color-success: #059669;
  --color-warning: #D97706;
  --color-error: #DC2626;
  --color-info: #2563EB;

  /* Backgrounds */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F9FAFB;
  --bg-card: #FFFFFF;
  --border-color: #E5E7EB;
}
```

### Typography

```css
/* Headings - Match report style */
.heading-1 {
  font-family: 'Georgia', serif;
  font-size: 2rem;
  font-weight: 400;
  color: var(--color-secondary-dark);
}

.heading-2 {
  font-family: 'Arial', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-primary);
}

/* Body Text */
.body-text {
  font-family: 'Arial', sans-serif;
  font-size: 0.875rem;
  color: var(--color-secondary);
  line-height: 1.5;
}

/* Metric Numbers */
.metric-value {
  font-family: 'Arial', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-secondary-dark);
}
```

---

## Page Layouts

### 1. Reports Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Reports Dashboard    [User ▼] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Total       │ │ Prayed on   │ │ Prophecies  │ │ Dreams      │   │
│  │ Attendance  │ │ Platform    │ │ Given       │ │ Interpreted │   │
│  │             │ │             │ │             │ │             │   │
│  │   1,247     │ │    312      │ │    156      │ │     23      │   │
│  │  ↑ 12%      │ │  ↑ 8%       │ │  ↑ 15%      │ │  ↓ 5%       │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────┐ ┌─────────────────────────┐   │
│  │  Attendance Trend (6 months)    │ │  Quick Actions          │   │
│  │  ┌───────────────────────────┐  │ │                         │   │
│  │  │     📈 Line Chart         │  │ │  [+ Enter Today's Data] │   │
│  │  │                           │  │ │                         │   │
│  │  │  Jan  Feb  Mar  Apr  May  │  │ │  [📄 Generate Report]   │   │
│  │  └───────────────────────────┘  │ │                         │   │
│  └─────────────────────────────────┘ │  [📧 Email Report]      │   │
│                                       │                         │   │
│  ┌─────────────────────────────────┐ │  [⚙️ Settings]          │   │
│  │  Sessions by Time Slot          │ └─────────────────────────┘   │
│  │  ┌───────────────────────────┐  │                               │
│  │  │  🟡 Morning    342        │  │  ┌─────────────────────────┐ │
│  │  │  🟢 Noon       298        │  │  │  Missing Data Alert     │ │
│  │  │  🔵 Evening    321        │  │  │                         │ │
│  │  │  🟣 Midnight   286        │  │  │  ⚠️ 3 sessions missing  │ │
│  │  │  🔴 Spanish     45        │  │  │  for this week          │ │
│  │  └───────────────────────────┘  │  │  [View Details →]       │ │
│  └─────────────────────────────────┘  └─────────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Recent Reports                                              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │ 📄 June 2025 Monthly Report    Jul 2  [Download] [📧] │  │   │
│  │  │ 📄 May 2025 Monthly Report     Jun 3  [Download] [📧] │  │   │
│  │  │ 📄 April 2025 Monthly Report   May 1  [Download] [📧] │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2. Metrics Entry Form (Prayer Team Leads)

**Desktop View:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Enter Metrics       [User ▼]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Enter Prayer Session Metrics                                       │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  📅 Date            │  │  🕐 Time Slot                       │  │
│  │  ┌───────────────┐  │  │  ┌─────────────────────────────┐   │  │
│  │  │ January 5, 2026│  │  │  │ 🟡 Morning Intimacy    ▼   │   │  │
│  │  └───────────────┘  │  │  └─────────────────────────────┘   │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Metrics                                                     │   │
│  │  ─────────────────────────────────────────────────────────  │   │
│  │                                                              │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ Total Room Count   │  │ Prayed on Platform │             │   │
│  │  │ (TC)               │  │ (PP)               │             │   │
│  │  │ ┌────────────────┐ │  │ ┌────────────────┐ │             │   │
│  │  │ │  [-]  25  [+]  │ │  │ │  [-]   8  [+]  │ │             │   │
│  │  │ └────────────────┘ │  │ └────────────────┘ │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  │                                                              │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ Prayer Requests    │  │ Prophesied         │             │   │
│  │  │ (PR)               │  │ (PS)               │             │   │
│  │  │ ┌────────────────┐ │  │ ┌────────────────┐ │             │   │
│  │  │ │  [-]   3  [+]  │ │  │ │  [-]   5  [+]  │ │             │   │
│  │  │ └────────────────┘ │  │ └────────────────┘ │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  │                                                              │   │
│  │  ┌────────────────────┐  ┌────────────────────┐             │   │
│  │  │ Prophecies Given   │  │ Dream Interp.      │             │   │
│  │  │ (PC)               │  │ (DI)               │             │   │
│  │  │ ┌────────────────┐ │  │ ┌────────────────┐ │             │   │
│  │  │ │  [-]   4  [+]  │ │  │ │  [-]   2  [+]  │ │             │   │
│  │  │ └────────────────┘ │  │ └────────────────┘ │             │   │
│  │  └────────────────────┘  └────────────────────┘             │   │
│  │                                                              │   │
│  │  ┌────────────────────┐                                     │   │
│  │  │ Dreams Interpreted │                                     │   │
│  │  │ (DC)               │                                     │   │
│  │  │ ┌────────────────┐ │                                     │   │
│  │  │ │  [-]   1  [+]  │ │                                     │   │
│  │  │ └────────────────┘ │                                     │   │
│  │  └────────────────────┘                                     │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  [Cancel]                              [Save Draft] [Submit] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ⏱️ Auto-saved 30 seconds ago                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Mobile View (Prayer Team Lead on-the-go):**
```
┌─────────────────────────┐
│  ← Back    Enter Data   │
├─────────────────────────┤
│                         │
│  📅 January 5, 2026     │
│                         │
│  ┌─────────────────────┐│
│  │ 🟡 Morning Intimacy ▼││
│  └─────────────────────┘│
│                         │
│  ─────────────────────  │
│                         │
│  Total Room Count (TC)  │
│  ┌─────────────────────┐│
│  │   [-]    25    [+]  ││
│  └─────────────────────┘│
│                         │
│  Prayed on Platform (PP)│
│  ┌─────────────────────┐│
│  │   [-]     8    [+]  ││
│  └─────────────────────┘│
│                         │
│  Prayer Requests (PR)   │
│  ┌─────────────────────┐│
│  │   [-]     3    [+]  ││
│  └─────────────────────┘│
│                         │
│  Prophesied (PS)        │
│  ┌─────────────────────┐│
│  │   [-]     5    [+]  ││
│  └─────────────────────┘│
│                         │
│  Prophecies Given (PC)  │
│  ┌─────────────────────┐│
│  │   [-]     4    [+]  ││
│  └─────────────────────┘│
│                         │
│  Dream Interp. (DI)     │
│  ┌─────────────────────┐│
│  │   [-]     2    [+]  ││
│  └─────────────────────┘│
│                         │
│  Dreams Interpreted (DC)│
│  ┌─────────────────────┐│
│  │   [-]     1    [+]  ││
│  └─────────────────────┘│
│                         │
│  ┌─────────────────────┐│
│  │      [Submit]       ││
│  └─────────────────────┘│
│                         │
└─────────────────────────┘
```

---

### 3. Weekly View (Admin Grid)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Weekly View              [User ▼]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ◀ Week of January 5 - 11, 2026 ▶          [Export] [Print]                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │        │  Sun  │  Mon  │  Tue  │  Wed  │  Thu  │  Fri  │  Sat  │TOTAL│   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │🟡Morn  │   -   │  25   │  23   │  28   │  21   │  24   │   -   │ 121 │   │
│  │  TC    │       │   8   │   7   │   9   │   6   │   8   │       │  38 │   │
│  │  PP    │       │   3   │   2   │   4   │   3   │   3   │       │  15 │   │
│  │  PR    │       │   5   │   4   │   6   │   4   │   5   │       │  24 │   │
│  │  PS    │       │   4   │   3   │   5   │   3   │   4   │       │  19 │   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │🟢Noon  │   -   │  18   │  20   │  22   │  19   │  21   │   -   │ 100 │   │
│  │  TC    │       │   5   │   6   │   7   │   5   │   6   │       │  29 │   │
│  │  PP    │       │   2   │   3   │   3   │   2   │   3   │       │  13 │   │
│  │  ...   │       │       │       │       │       │       │       │     │   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │🔵Eve   │   -   │  15   │  17   │  19   │  16   │  18   │   -   │  85 │   │
│  │  TC    │       │   4   │   5   │   6   │   4   │   5   │       │  24 │   │
│  │  ...   │       │       │       │       │       │       │       │     │   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │🟣Mid   │   -   │  12   │  14   │  13   │  11   │  15   │   -   │  65 │   │
│  │  TC    │       │   3   │   4   │   4   │   3   │   4   │       │  18 │   │
│  │  ...   │       │       │       │       │       │       │       │     │   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │🔴Span  │   -   │   -   │   8   │   -   │   9   │   -   │   -   │  17 │   │
│  │  TC    │       │       │   2   │       │   3   │       │       │   5 │   │
│  │  ...   │       │       │       │       │       │       │       │     │   │
│  ├────────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────┤   │
│  │ DAILY  │   0   │  70   │  82   │  82   │  76   │  78   │   0   │ 388 │   │
│  │ TOTAL  │       │       │       │       │       │       │       │     │   │
│  └────────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴─────┘   │
│                                                                             │
│  Legend: TC=Total Count  PP=Prayed Platform  PR=Prayer Req  PS=Prophesied   │
│          PC=Prophecies   DI=Dream Interp    DC=Dreams Count                 │
│                                                                             │
│  ⚠️ Missing: Sunday (all), Saturday (all)                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Cell States:**
- Empty cell: Light red background (#FEE2E2)
- Filled cell: White background
- Today's cell: Light blue border
- Selected cell: Blue highlight

---

### 4. Generate Report Page

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Generate Report    [User ▼]   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Generate Ministry Report                                           │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Report Type                                                 │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │  ○ Weekly Summary                                    │    │   │
│  │  │  ● Monthly Report (matches current PDF format)       │    │   │
│  │  │  ○ Quarterly Review                                  │    │   │
│  │  │  ○ Annual Report                                     │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Period                                                      │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐           │   │
│  │  │  Month:  June    ▼  │  │  Year:  2025     ▼  │           │   │
│  │  └─────────────────────┘  └─────────────────────┘           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Include Sections                                            │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │  ☑️ Daily Prayer Statistics                          │    │   │
│  │  │  ☑️ Regular Weekly Classes                           │    │   │
│  │  │  ☑️ Special Classes & Events                         │    │   │
│  │  │  ☑️ Supernatural Sundays Summary                     │    │   │
│  │  │  ☑️ Ministry Totals (People Ministered, Salvations)  │    │   │
│  │  │  ☑️ Contact Information                              │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Export Format                                               │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │  ☑️ PDF Document (.pdf)                              │    │   │
│  │  │  ☑️ Word Document (.docx)                            │    │   │
│  │  │  ☐ Excel Spreadsheet (.xlsx)                         │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                     [Preview Report]  [Generate & Download]         │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PREVIEW                                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │      🔥 SCHOOL OF THE                               │    │   │
│  │  │         HOLY SPIRIT                                  │    │   │
│  │  │                                                      │    │   │
│  │  │  School of The Holy Spirit  Monthly Activity: Report │    │   │
│  │  │                                                      │    │   │
│  │  │  June 2025 (all hours given are monthly totals)      │    │   │
│  │  │  ● Date: July 2, 2025                                │    │   │
│  │  │                                                      │    │   │
│  │  │  ● Regular Daily Prayer    ● Supernatural Sunday     │    │   │
│  │  │  ● Regular Weekly Classes  ● Special Classes         │    │   │
│  │  │                                                      │    │   │
│  │  │  x4 times a Day Prayers...                           │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  │                                                              │   │
│  │  Page 1 of 3                          [Zoom -] [Zoom +]      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 5. Admin Settings - Metric Types CRUD

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Settings > Metrics  [User ▼]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Metric Types Configuration                    [+ Add New Metric]   │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ≡  │ Code │ Display Name          │ Type    │ Report │ ⚡  │   │
│  ├─────┼──────┼───────────────────────┼─────────┼────────┼─────┤   │
│  │  ≡  │ TC   │ Total Room Count      │ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ PP   │ Prayed on Platform    │ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ PR   │ Prayer Request Count  │ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ PS   │ Prophesied            │ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ PC   │ Prophecies Given      │ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ DI   │ Dream Interp. Provided│ Integer │   ✓    │ [✎]│   │
│  │  ≡  │ DC   │ Dreams Interpreted    │ Integer │   ✓    │ [✎]│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  💡 Drag rows (≡) to reorder. Changes save automatically.          │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Edit Metric: Total Room Count                              [×]     │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │ Code *              │  │ Display Name *                      │  │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────────────┐ │  │
│  │ │ TC              │ │  │ │ Total Room Count                │ │  │
│  │ └─────────────────┘ │  │ └─────────────────────────────────┘ │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Description                                                  │   │
│  │ ┌─────────────────────────────────────────────────────────┐ │   │
│  │ │ Number of attendees present in the prayer room          │ │   │
│  │ └─────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │ Data Type           │  │ Options             │                  │
│  │ ┌─────────────────┐ │  │ ☑️ Required         │                  │
│  │ │ Integer      ▼  │ │  │ ☑️ Show on Report   │                  │
│  │ └─────────────────┘ │  │ ☑️ Active           │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│                              [Cancel]  [Delete]  [Save Changes]     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 6. Admin Settings - Time Slots CRUD

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo] School of The Holy Spirit    Settings > Time Slots [User ▼]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Time Slots Configuration                     [+ Add New Time Slot] │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ≡  │ ● │ Display Name        │ Typical Time     │ Active │⚡│   │
│  ├─────┼───┼─────────────────────┼──────────────────┼────────┼──┤   │
│  │  ≡  │🟡 │ Morning Intimacy    │ 6:00 AM EST      │   ✓    │[✎]│  │
│  │  ≡  │🟢 │ Noon Day            │ 12:00 PM EST     │   ✓    │[✎]│  │
│  │  ≡  │🔵 │ Evening Incense     │ 6:00 PM EST      │   ✓    │[✎]│  │
│  │  ≡  │🟣 │ Midnight Watch      │ 12:00 AM EST     │   ✓    │[✎]│  │
│  │  ≡  │🔴 │ Spanish             │ Varies           │   ✓    │[✎]│  │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  💡 Drag rows (≡) to reorder display order.                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Edit Time Slot: Morning Intimacy                           [×]     │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────────────────────┐  │
│  │ Slot Code *         │  │ Display Name *                      │  │
│  │ ┌─────────────────┐ │  │ ┌─────────────────────────────────┐ │  │
│  │ │ morning         │ │  │ │ Morning Intimacy                │ │  │
│  │ └─────────────────┘ │  │ └─────────────────────────────────┘ │  │
│  └─────────────────────┘  └─────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │ Typical Time        │  │ Color               │                  │
│  │ ┌─────────────────┐ │  │ ┌─────────────────┐ │                  │
│  │ │ 6:00 AM EST     │ │  │ │ 🟡 #F59E0B      │ │                  │
│  │ └─────────────────┘ │  │ └─────────────────┘ │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│  ┌─────────────────────┐                                           │
│  │ Options             │                                           │
│  │ ☑️ Active           │                                           │
│  └─────────────────────┘                                           │
│                                                                     │
│                              [Cancel]  [Delete]  [Save Changes]     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Library

### 1. Metric Card

```jsx
// Usage: Dashboard summary cards
<MetricCard
  title="Total Attendance"
  value={1247}
  change={+12}        // percentage change
  icon="👥"
  color="primary"
/>
```

```
┌─────────────────────┐
│  👥                 │
│  Total Attendance   │
│                     │
│     1,247           │
│                     │
│  ↑ 12% vs last mo   │
└─────────────────────┘
```

### 2. Stepper Input (Mobile-friendly)

```jsx
// Usage: Metric entry form
<StepperInput
  label="Total Room Count"
  code="TC"
  value={25}
  min={0}
  onChange={setValue}
/>
```

```
┌─────────────────────────┐
│  Total Room Count (TC)  │
│  ┌─────────────────────┐│
│  │  [-]    25    [+]   ││
│  └─────────────────────┘│
└─────────────────────────┘
```

### 3. Time Slot Selector

```jsx
// Usage: Dropdown with color indicators
<TimeSlotSelector
  value="morning"
  onChange={setSlot}
  slots={timeSlots}
/>
```

```
┌──────────────────────────────┐
│  🟡 Morning Intimacy      ▼  │
├──────────────────────────────┤
│  🟡 Morning Intimacy         │
│  🟢 Noon Day                 │
│  🔵 Evening Incense          │
│  🟣 Midnight Watch           │
│  🔴 Spanish                  │
└──────────────────────────────┘
```

### 4. Data Grid Cell

```jsx
// Usage: Weekly view grid
<GridCell
  value={25}
  isEmpty={false}
  isToday={true}
  onClick={handleEdit}
/>
```

States:
- Empty: `bg-red-50 text-gray-400`
- Filled: `bg-white text-gray-900`
- Today: `border-2 border-blue-500`
- Selected: `bg-blue-50`

### 5. Report Preview Frame

```jsx
// Usage: Generate report page
<ReportPreview
  html={reportHtml}
  currentPage={1}
  totalPages={3}
  onZoom={handleZoom}
/>
```

---

## Report Output Format (Matching Existing PDF)

### Page Structure

**Page 1: Prayer & Classes**
```
┌─────────────────────────────────────────────────────────────┐
│                    [LOGO - Fire/Wings]                      │
│                                                             │
│  School of The Holy Spirit    Monthly Activity: Report      │
│                                                             │
│  June 2025 (all hours given are monthly totals)             │
│  ● Date: July 2, 2025                                       │
│                                                             │
│  ● Regular Daily Prayer    ● Supernatural Sunday            │
│  ● Regular Weekly Classes  ● Special Classes & Projects     │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  x4 times a Day Prayers          ● Description: These...    │
│  (6am, 12noon, 6pm, 12midnight)                             │
│                                                             │
│  1. Morning Intimacy (6 am)        31 hours                 │
│  2. Noon Day Prayers (12noon)      Temporarily Stopped      │
│  3. Evening Incense (6pm)          25 hours                 │
│  4. Midnight Watch (12 am)         Temporarily Stopped      │
│     Joseph's Tunic                 2 hours 2x/week          │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Regular Weekly Classes (10 am)    ● Description: These...  │
│  Prophetic Training & Activations  Temporarily Stopped      │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                     SCHOOL OF THE HOLY SPIRIT 1│
└─────────────────────────────────────────────────────────────┘
```

**Page 2: Classes & Events**
```
┌─────────────────────────────────────────────────────────────┐
│                    [LOGO - Fire/Wings]                      │
│                                                             │
│  Revelatory Reading                8 hours                  │
│  Monday Evenings Mentoring         10 hours                 │
│  Monday (Teaching)                                          │
│  School of the Prophets            Temporarily Halted       │
│  SOZO                              None Completed           │
│  Prophets & Seers Training         0                        │
│  Prophetic                         0                        │
│  Kingdom of God                    0                        │
│  Worship & Soaking                 0                        │
│  School of the Priests             Temporarily Halted       │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Special Pop-Up Classes            ● Description: These...  │
│  Pastoral Care & Meetings          40 hours Principal       │
│  Priest & Kings Conference         51 hours                 │
│  Conference Travel Time            23 hr round trip         │
│  oración en la mañana                                       │
│  oración e Intimidad con Jesús                              │
│  Atlanta Local Missions                                     │
│  Columbia, SC Local Missions                                │
│  Corporate Deliverance                                      │
│  Individual Deliverance                                     │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                     SCHOOL OF THE HOLY SPIRIT 2│
└─────────────────────────────────────────────────────────────┘
```

**Page 3: Summary & Contact**
```
┌─────────────────────────────────────────────────────────────┐
│                    [LOGO - Fire/Wings]                      │
│                                                             │
│  Supernatural Sundays              ● Description: This...   │
│                                                             │
│  Total people Ministered to:       totals 1065              │
│  Total New Salvations:                                      │
│  Prayer Requests:                                           │
│  Praise Reports/Testimonials:                               │
│  Verified Ministry Efficacy:       Approximately 40         │
│  ORCA Donations by Jane Smith      $55.50                   │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  New Members Meeting                                        │
│                                                             │
│  ┌─────────┐  Seeking the kingdom and His righteousness...  │
│  │ [Image] │  Those who are really hungry and thirsty...    │
│  │Discover │  He will clothe you with His righteousness...  │
│  └─────────┘                                                │
│                                                             │
│  Find out more on schooloftheHolySpirit.club                │
│                                                             │
│  Contact Information                                        │
│  ATTN: School Of The Holy Spirit Church                     │
│  P.O. Box 1197,                                             │
│  Irmo, SC 29063                                             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                     SCHOOL OF THE HOLY SPIRIT 3│
└─────────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px) {  /* sm */ }
@media (min-width: 768px) {  /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Dashboard Grid
- **Mobile (< 640px)**: 1 column, stacked cards
- **Tablet (640-1024px)**: 2 columns
- **Desktop (> 1024px)**: 4 columns for metric cards

### Weekly View Grid
- **Mobile**: Horizontal scroll, fixed first column
- **Tablet+**: Full grid visible

### Forms
- **Mobile**: Single column, full-width inputs
- **Desktop**: Two-column layout for metric inputs

---

## Accessibility Notes

1. **Color contrast**: All text meets WCAG AA standards
2. **Focus indicators**: Visible focus rings on all interactive elements
3. **Screen readers**: All icons have aria-labels
4. **Keyboard navigation**: Full tab support for all forms
5. **Touch targets**: Minimum 44x44px for mobile buttons

---

*Design specification for Admin Reporting System - January 5, 2026*
