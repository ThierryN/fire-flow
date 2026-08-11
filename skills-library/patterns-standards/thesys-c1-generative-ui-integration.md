# Thesys C1: Generative UI Integration for LLM-Powered Apps

**Skill Name**: `thesys-c1-generative-ui-integration`
**Category**: AI/UI Integration
**Last Updated**: October 28, 2025
**Status**: Production-Ready (Launched April 2025)

---

## Overview

**C1 by Thesys** is an API middleware that transforms Large Language Model (LLM) text responses into interactive, real-time user interfaces. Instead of rendering walls of text, C1 generates structured UI components like forms, charts, tables, and cards that users can interact with directly.

**Key Value Proposition**:
- 🚀 Build AI frontends **10x faster** and **80% cheaper**
- 📊 **83% of users** find C1 responses more engaging than text
- ⚡ Real-time streaming UI (components appear progressively)
- 🔄 OpenAI-compatible API (drop-in replacement)
- 🎨 Fully customizable to match your design system

**Official Resources**:
- Website: https://www.thesys.dev
- Documentation: https://docs.thesys.dev
- Console (API Keys): https://console.thesys.dev
- Demo Playground: https://demo.thesys.dev
- Quick Start: `npx create-c1-app`

---

## What C1 Does

### Traditional LLM Response:
```
"Here's your budget analysis:
- Total income: $5,000
- Total expenses: $4,200
- Remaining: $800
You're spending 84% of your income..."
```

### C1 Response (Generative UI):
```jsx
<Card>
  <ProgressChart
    data={[
      { label: 'Income', value: 5000, color: 'green' },
      { label: 'Expenses', value: 4200, color: 'red' }
    ]}
  />
  <Form onSubmit={handleBudgetAdjustment}>
    <Input label="Adjust Budget" />
    <Button>Update</Button>
  </Form>
  <Alert severity="warning">
    You're spending 84% of your income. Consider reducing expenses.
  </Alert>
</Card>
```

**Result**: Users see live, interactive components instead of text they have to parse.

---

## Use Cases for Budget App

### 1. **Interactive Budget Visualization**
Instead of displaying budget data as text, C1 can generate:
- Live pie charts showing expense categories
- Bar graphs comparing monthly spending
- Interactive sliders to adjust budget allocations
- Real-time updates as user changes values

### 2. **Dynamic Form Generation**
- Generate expense entry forms based on category
- Multi-step wizards for complex transactions
- Conditional fields that appear based on user input
- Form validation with instant feedback

### 3. **Intelligent Data Tables**
- Sortable, filterable transaction tables
- Inline editing of expenses
- Clickable rows that expand for details
- Export buttons for CSV/PDF

### 4. **AI-Powered Recommendations**
- Interactive cards suggesting budget optimizations
- Clickable actions ("Reduce dining by 15%")
- Comparison views (current vs. recommended)
- Progress tracking towards savings goals

### 5. **OIC Document Generation**
- Step-by-step forms for Form 656 completion
- Interactive calculators for RCP (Reasonable Collection Potential)
- Real-time validation of GTA form fields
- Generated PDF previews with edit capabilities

---

## How It Works

### Architecture

```
Your App
    ↓
LLM (OpenAI, Claude, etc.)
    ↓
C1 API Middleware (api.thesys.dev)
    ↓
Structured UI Components (JSON)
    ↓
C1 React SDK
    ↓
Rendered Interactive UI
```

**Key Difference**:
- **Traditional**: LLM → Text → Your code parses text → Render UI
- **C1**: LLM → C1 API → Structured Components → Instant Render

---

## Integration Steps

### Step 1: Get API Key

1. Go to https://console.thesys.dev
2. Sign up / Log in
3. Generate API key
4. Copy key to environment variables

```bash
THESYS_API_KEY=your_api_key_here
```

### Step 2: Install Dependencies

```bash
# Option 1: Quick start (creates new project)
npx create-c1-app my-app

# Option 2: Add to existing project
npm install @thesys/react-sdk
# or
yarn add @thesys/react-sdk
# or
pnpm add @thesys/react-sdk
```

### Step 3: Update API Endpoint

**Before (OpenAI)**:
```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const completion = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [
    { role: "user", content: "Show me my budget breakdown" }
  ]
});
```

**After (Thesys C1)**:
```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.THESYS_API_KEY,
  baseURL: "https://api.thesys.dev/v1/embed" // <-- Only change!
});

const completion = await openai.chat.completions.create({
  model: "gpt-4", // Still use your preferred model
  messages: [
    { role: "user", content: "Show me my budget breakdown" }
  ]
});

// Response now includes structured UI components!
```

### Step 4: Render with C1 React SDK

```tsx
import { C1Component } from '@thesys/react-sdk';

function BudgetAnalysis() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (userMessage: string) => {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        ...messages,
        { role: "user", content: userMessage }
      ],
      stream: true // Enable streaming for real-time UI
    });

    // C1 handles the rendering automatically
    for await (const chunk of completion) {
      // UI components appear progressively
    }
  };

  return (
    <div>
      <C1Component
        messages={messages}
        onInteraction={(data) => {
          // Handle button clicks, form submissions, etc.
          console.log('User interacted:', data);
        }}
      />
    </div>
  );
}
```

---

## Advanced Features

### 1. Custom Components

Bring your own React components:

```tsx
import { registerComponent } from '@thesys/react-sdk';

// Register custom budget card component
registerComponent('BudgetCard', ({ income, expenses }) => (
  <div className="budget-card">
    <h3>Monthly Overview</h3>
    <div className="income">Income: ${income}</div>
    <div className="expenses">Expenses: ${expenses}</div>
    <div className="remaining">
      Remaining: ${income - expenses}
    </div>
  </div>
));

// Now C1 can generate <BudgetCard /> components
```

### 2. Tool Calls / Function Calling

Connect C1 to your database:

```typescript
const completion = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [...],
  tools: [
    {
      type: "function",
      function: {
        name: "get_transactions",
        description: "Get user's recent transactions",
        parameters: {
          type: "object",
          properties: {
            startDate: { type: "string" },
            endDate: { type: "string" },
            category: { type: "string" }
          }
        }
      }
    }
  ]
});

// C1 can call this function and use the data to generate UI
```

### 3. Theme Customization

Match your design system:

```tsx
import { C1Provider } from '@thesys/react-sdk';

function App() {
  return (
    <C1Provider
      theme={{
        primaryColor: '#3B82F6',
        fontFamily: 'Inter, sans-serif',
        borderRadius: '8px',
        darkMode: true
      }}
    >
      <YourApp />
    </C1Provider>
  );
}
```

### 4. Real-Time Streaming

Components appear as they're generated:

```typescript
const stream = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [...],
  stream: true // Enable progressive rendering
});

for await (const chunk of stream) {
  // Chart appears...
  // Then form appears...
  // Then table appears...
  // All in real-time!
}
```

---

## Integration with Budget App

### Scenario 1: Budget Analysis Chat

**User**: "Analyze my spending this month"

**C1 Response** (Generated UI):
```tsx
<Dashboard>
  <PieChart
    title="Expense Breakdown"
    data={[
      { category: 'Food', amount: 450, color: '#FF6384' },
      { category: 'Transport', amount: 200, color: '#36A2EB' },
      { category: 'Entertainment', amount: 150, color: '#FFCE56' }
    ]}
    interactive={true}
    onClick={(category) => showCategoryDetails(category)}
  />

  <Alert severity="warning">
    Your food expenses are 28% higher than last month
  </Alert>

  <ActionButtons>
    <Button onClick={() => setbudget('food', 400)}>
      Set Food Budget to $400
    </Button>
    <Button onClick={() => viewRecommendations()}>
      View Savings Tips
    </Button>
  </ActionButtons>
</Dashboard>
```

### Scenario 2: OIC Form Assistant

**User**: "Help me fill out Form 656"

**C1 Response** (Generated UI):
```tsx
<Form title="Form 656 - Offer in Compromise">
  <Step number={1} title="Personal Information">
    <Input
      label="Name"
      value={user.name}
      required={true}
    />
    <Input
      label="SSN"
      type="ssn"
      mask="XXX-XX-XXXX"
      required={true}
    />
  </Step>

  <Step number={2} title="Offer Amount">
    <Calculator
      description="Based on your RCP calculation"
      formula="Future Income + Net Equity"
      result={8000}
    />
    <Input
      label="Offer Amount"
      type="currency"
      suggested={8000}
      min={1000}
    />
  </Step>

  <Navigation>
    <Button variant="secondary">Previous</Button>
    <Button variant="primary">Next</Button>
  </Navigation>
</Form>
```

### Scenario 3: Transaction Management

**User**: "Show my October expenses"

**C1 Response** (Generated UI):
```tsx
<DataTable
  title="October 2025 Expenses"
  columns={[
    { key: 'date', label: 'Date', sortable: true },
    { key: 'description', label: 'Description', searchable: true },
    { key: 'category', label: 'Category', filterable: true },
    { key: 'amount', label: 'Amount', sortable: true, format: 'currency' }
  ]}
  data={transactions}
  actions={[
    { label: 'Edit', icon: 'pencil', onClick: editTransaction },
    { label: 'Delete', icon: 'trash', onClick: deleteTransaction },
    { label: 'Split', icon: 'split', onClick: splitTransaction }
  ]}
  pagination={true}
  exportFormats={['CSV', 'PDF', 'Excel']}
/>
```

---

## Best Practices

### 1. Prompting for UI Generation

**❌ Bad Prompt**:
```
"Show me the budget"
```

**✅ Good Prompt**:
```
"Create an interactive budget dashboard with:
1. A pie chart showing expense categories
2. A bar graph comparing this month vs last month
3. An editable table of all transactions
4. Action buttons to set budget limits
5. Alerts for categories over budget"
```

**Why**: Specific prompts generate better structured UI.

### 2. Handle User Interactions

```tsx
<C1Component
  messages={messages}
  onInteraction={(interaction) => {
    switch (interaction.type) {
      case 'button_click':
        handleButtonClick(interaction.data);
        break;
      case 'form_submit':
        handleFormSubmit(interaction.data);
        break;
      case 'chart_click':
        showDetails(interaction.data);
        break;
    }
  }}
/>
```

### 3. Error Handling

C1 has built-in error handling, but you should still:

```tsx
try {
  const completion = await openai.chat.completions.create({...});
} catch (error) {
  if (error.status === 401) {
    console.error('Invalid Thesys API key');
  } else if (error.status === 429) {
    console.error('Rate limit exceeded');
  } else {
    console.error('C1 API error:', error);
  }
}
```

### 4. Fallback to Text

If C1 is unavailable, fall back to traditional text:

```tsx
const USE_C1 = process.env.ENABLE_C1 === 'true';

const baseURL = USE_C1
  ? "https://api.thesys.dev/v1/embed"
  : "https://api.openai.com/v1";

const openai = new OpenAI({ apiKey, baseURL });
```

---

## Performance Optimization

### 1. Streaming for Responsiveness

Always enable streaming for progressive UI rendering:

```typescript
const completion = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [...],
  stream: true // Components appear as generated
});
```

### 2. Caching Common Components

Cache frequently generated UI components:

```tsx
import { cacheComponent } from '@thesys/react-sdk';

// Cache budget dashboard for 5 minutes
cacheComponent('budget-dashboard', budgetData, { ttl: 300 });
```

### 3. Lazy Loading

Load C1 SDK only when needed:

```tsx
const C1Component = lazy(() => import('@thesys/react-sdk').then(m => ({ default: m.C1Component })));

<Suspense fallback={<Loading />}>
  <C1Component messages={messages} />
</Suspense>
```

---

## Security Considerations

### 1. API Keys

```typescript
// ✅ GOOD: Server-side API calls
// backend/api/chat.ts
const openai = new OpenAI({
  apiKey: process.env.THESYS_API_KEY, // Server env variable
  baseURL: "https://api.thesys.dev/v1/embed"
});

// ❌ BAD: Client-side API calls
// NEVER expose API keys in frontend code
```

### 2. User Data

C1 by Thesys claims:
- ✅ Zero data retention
- ✅ SOC2 compliant
- ✅ GDPR compliant
- ✅ ISO 27001 certified
- ✅ Private deployment options available

Still follow best practices:
- Don't send sensitive data (SSNs, passwords) in prompts
- Sanitize user inputs
- Use encryption for data in transit

### 3. Rate Limiting

Implement rate limiting on your API endpoints:

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // Max 100 requests per 15 min
});

app.use('/api/chat', limiter);
```

---

## Pricing & Limits

**Note**: Check https://console.thesys.dev for current pricing.

**As of April 2025**:
- Free tier available for testing
- Pay-as-you-go based on API calls
- Enterprise plans with private deployment
- **Claims 80% cheaper than building custom UI**

**Typical Cost Breakdown**:
- C1 API call: ~$0.01-0.05 per request (includes UI generation)
- Traditional approach: Developer time ($50-200/hr) × hours building UI
- **ROI**: Significant savings on development time

---

## Comparison: Traditional vs C1

### Traditional LLM Integration:

```typescript
// 1. Call LLM
const response = await openai.chat.completions.create({...});

// 2. Parse response text
const data = parseResponseText(response.content);

// 3. Manually create UI components
return (
  <div>
    <h3>{data.title}</h3>
    <Chart data={data.chartData} />
    <Table data={data.tableData} />
    <Form fields={data.formFields} />
  </div>
);

// Result: Lots of custom code, brittle parsing, slow development
```

### C1 Integration:

```typescript
// 1. Call C1 API (same OpenAI SDK!)
const response = await openai.chat.completions.create({
  baseURL: "https://api.thesys.dev/v1/embed"
  // ... same parameters
});

// 2. Render with C1 SDK
return <C1Component messages={[response]} />;

// Result: UI appears automatically, no parsing, fast development
```

**Developer Time**:
- Traditional: 2-4 hours per UI component
- C1: 10 minutes to integrate, 0 time per component

---

## Compatibility

### Supported LLMs:
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude 3.5, Claude 3)
- ✅ Google (Gemini)
- ✅ Mistral
- ✅ Llama (via Groq, Together AI)
- ✅ Any OpenAI-compatible API

### Supported Frameworks:
- ✅ React (primary SDK)
- ✅ Next.js
- ✅ Remix
- ✅ Vite
- ⏳ Vue (community SDK in development)
- ⏳ Svelte (community SDK in development)

### Supported UI Components:
- Charts (pie, bar, line, area, scatter)
- Forms (inputs, selects, checkboxes, radio buttons)
- Tables (sortable, filterable, paginated)
- Cards (info cards, stat cards, action cards)
- Alerts (success, warning, error, info)
- Buttons (primary, secondary, danger)
- Modals (dialogs, confirmations)
- Tabs (navigation, content switching)
- Lists (ordered, unordered, checkboxes)
- Progress bars, spinners, loaders
- Custom components (bring your own)

---

## Example: Full Integration in Budget App

### 1. Backend API Route

```typescript
// app/api/chat/route.ts
import OpenAI from 'openai';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  const { message } = await req.json();

  const openai = new OpenAI({
    apiKey: process.env.THESYS_API_KEY!,
    baseURL: "https://api.thesys.dev/v1/embed"
  });

  const completion = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      {
        role: "system",
        content: `You are a budget analysis assistant. Generate interactive UI components to help users understand their finances. Use:
        - Charts for visual data
        - Tables for transaction lists
        - Forms for data entry
        - Alerts for important insights
        - Buttons for actions`
      },
      {
        role: "user",
        content: message
      }
    ],
    stream: true,
    tools: [
      {
        type: "function",
        function: {
          name: "get_transactions",
          description: "Fetch user transactions from database",
          parameters: {
            type: "object",
            properties: {
              startDate: { type: "string" },
              endDate: { type: "string" }
            }
          }
        }
      }
    ]
  });

  return new NextResponse(completion.toReadableStream());
}
```

### 2. Frontend Component

```tsx
// app/components/BudgetChat.tsx
'use client';

import { useState } from 'react';
import { C1Component } from '@thesys/react-sdk';

export default function BudgetChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      let assistantMessage = { role: 'assistant', content: '' };

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        assistantMessage.content += chunk;

        // Update messages in real-time (streaming)
        setMessages(prev => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          if (newMessages[lastIndex]?.role === 'assistant') {
            newMessages[lastIndex] = assistantMessage;
          } else {
            newMessages.push(assistantMessage);
          }
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="budget-chat">
      <div className="messages">
        <C1Component
          messages={messages}
          onInteraction={(data) => {
            // Handle UI interactions
            console.log('User interacted:', data);
            if (data.type === 'button_click') {
              sendMessage(data.action);
            }
          }}
        />
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about your budget..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

### 3. Configure C1 Provider

```tsx
// app/layout.tsx
import { C1Provider } from '@thesys/react-sdk';
import '@thesys/react-sdk/dist/styles.css'; // Import C1 styles

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <C1Provider
          theme={{
            primaryColor: '#3B82F6',
            fontFamily: 'Inter, system-ui, sans-serif',
            borderRadius: '8px',
            darkMode: true
          }}
        >
          {children}
        </C1Provider>
      </body>
    </html>
  );
}
```

---

## Troubleshooting

### Issue: Components not rendering

**Cause**: Missing C1 React SDK or incorrect import

**Solution**:
```bash
npm install @thesys/react-sdk
```

```tsx
import { C1Component } from '@thesys/react-sdk';
import '@thesys/react-sdk/dist/styles.css'; // Don't forget styles!
```

### Issue: API returns text instead of UI components

**Cause**: Not using C1 API endpoint

**Solution**:
```typescript
const openai = new OpenAI({
  apiKey: process.env.THESYS_API_KEY,
  baseURL: "https://api.thesys.dev/v1/embed" // Must use this URL!
});
```

### Issue: Components look unstyled

**Cause**: Missing CSS import

**Solution**:
```tsx
import '@thesys/react-sdk/dist/styles.css';
```

### Issue: Slow rendering

**Cause**: Not using streaming

**Solution**:
```typescript
const completion = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [...],
  stream: true // Enable streaming!
});
```

---

## When to Use C1

### ✅ USE C1 When:
- Building AI-powered dashboards
- Creating conversational UIs with data visualization
- Need interactive forms generated from AI
- Want to prototype AI UIs quickly
- Building customer-facing AI agents
- Need real-time, dynamic interfaces

### ❌ DON'T USE C1 When:
- Building static content sites
- UI requirements are very simple (just text chat)
- Need full control over every pixel (design-heavy apps)
- Working with non-LLM data sources
- Budget is extremely constrained (though C1 claims 80% savings)

---

## Conclusion

**C1 by Thesys is a game-changer for AI-powered applications**. It eliminates the tedious work of:
1. Parsing LLM text outputs
2. Manually building UI components
3. Wiring up interactions
4. Maintaining complex prompt-to-UI logic

**For the Budget App**, C1 could transform:
- Budget analysis (text → interactive dashboards)
- Transaction management (lists → sortable tables)
- Form completion (text guidance → step-by-step wizards)
- Financial recommendations (suggestions → clickable actions)

**Getting Started**:
```bash
npx create-c1-app budget-app-c1
cd budget-app-c1
npm run dev
```

**Next Steps**:
1. Get API key from https://console.thesys.dev
2. Try the demo at https://demo.thesys.dev
3. Read docs at https://docs.thesys.dev
4. Integrate into budget app (start with one feature)
5. Expand to more features based on success

---

**Skill Created**: October 28, 2025
**Maintainer**: Claude Code
**License**: Skill documentation for educational purposes. C1 by Thesys is a commercial product.
