# Batch Operations with Progress Modal & Checkbox Selection - Implementation Guide

## The Problem

Admin pages often need to perform the same action on multiple items (e.g., sending reports to multiple students, bulk emails, mass updates). Building this requires three interconnected patterns:

1. **Checkbox selection** — Let users pick which items to act on
2. **Batch processing** — Execute the action for each selected item sequentially
3. **Progress modal** — Show real-time feedback so users know what's happening

### Why It Was Hard

- Checkbox selection needs `stopPropagation` when rows are clickable (navigation)
- Batch operations need error handling per-item (one failure shouldn't stop all)
- Progress modal needs real-time updates during async loop
- Select-all must sync with individual checkboxes
- Button labels should reflect selection state dynamically

### Impact

Without this pattern, admins must manually process each student/item one at a time — clicking, waiting, going back, repeating. With 30+ students per course, this is unacceptable.

---

## The Solution

### Pattern 1: Checkbox Bulk Selection

```jsx
// State
const [selectedStudents, setSelectedStudents] = useState(new Set());

// Toggle individual
const toggleStudent = (id) => {
  setSelectedStudents(prev => {
    const next = new Set(prev);
    next.has(id) ? next.delete(id) : next.add(id);
    return next;
  });
};

// Toggle all
const toggleAll = () => {
  if (selectedStudents.size === students.length) {
    setSelectedStudents(new Set());
  } else {
    setSelectedStudents(new Set(students.map(s => s.id)));
  }
};
```

#### Table Header (Select-All)
```jsx
<th className="...">
  <input
    type="checkbox"
    checked={selectedStudents.size === students.length && students.length > 0}
    onChange={toggleAll}
    className="rounded border-slate-600 bg-slate-700 text-blue-500
               focus:ring-blue-500 focus:ring-offset-0 cursor-pointer"
  />
</th>
```

#### Table Row (Per-Item Checkbox)

**CRITICAL: `stopPropagation` prevents row click navigation**

```jsx
<td className="..." onClick={(e) => e.stopPropagation()}>
  <input
    type="checkbox"
    checked={selectedStudents.has(student.id)}
    onChange={() => toggleStudent(student.id)}
    className="rounded border-slate-600 bg-slate-700 text-blue-500
               focus:ring-blue-500 focus:ring-offset-0 cursor-pointer"
  />
</td>
```

#### Selection Bar (appears when items selected)
```jsx
{selectedStudents.size > 0 && (
  <div className="flex items-center gap-3 px-4 py-2 bg-blue-500/10
                  border border-blue-500/30 rounded-lg mb-4">
    <span className="text-blue-400 text-sm font-medium">
      {selectedStudents.size} student{selectedStudents.size > 1 ? 's' : ''} selected
    </span>
    <button
      onClick={() => setSelectedStudents(new Set())}
      className="text-xs text-slate-400 hover:text-white"
    >
      Clear
    </button>
  </div>
)}
```

#### Smart Button Label
```jsx
<button onClick={handleBatchAction}>
  {selectedStudents.size > 0
    ? `Send Report (${selectedStudents.size})`
    : `Send Report to All (${students.length})`
  }
</button>
```

---

### Pattern 2: Batch Processing with Per-Item Error Handling

```jsx
const [batchState, setBatchState] = useState({
  running: false,
  progress: [],    // { id, name, status: 'pending'|'sending'|'done'|'error', result }
  current: 0,
  total: 0
});

const handleBatchAction = async () => {
  // Determine target list
  const targets = selectedStudents.size > 0
    ? items.filter(i => selectedStudents.has(i.id))
    : items;

  if (targets.length === 0) return;

  // Initialize progress
  setBatchState({
    running: true,
    progress: targets.map(t => ({
      id: t.id,
      name: t.name,
      status: 'pending',
      result: null
    })),
    current: 0,
    total: targets.length
  });

  // Process sequentially (not parallel — avoid rate limits)
  for (let i = 0; i < targets.length; i++) {
    const target = targets[i];

    // Update status to "sending"
    setBatchState(prev => ({
      ...prev,
      current: i + 1,
      progress: prev.progress.map(p =>
        p.id === target.id ? { ...p, status: 'sending' } : p
      )
    }));

    try {
      // ---- Your batch action here ----
      const detail = await fetchDetail(target.id);
      const result = await processItem(detail);
      await sendResult(target.id, result);
      // ---------------------------------

      setBatchState(prev => ({
        ...prev,
        progress: prev.progress.map(p =>
          p.id === target.id ? { ...p, status: 'done', result } : p
        )
      }));
    } catch (err) {
      console.error(`Failed for ${target.name}:`, err);
      setBatchState(prev => ({
        ...prev,
        progress: prev.progress.map(p =>
          p.id === target.id ? { ...p, status: 'error', result: err.message } : p
        )
      }));
      // Continue to next item (don't break!)
    }
  }

  // Mark batch as complete (keep modal open for review)
  setBatchState(prev => ({ ...prev, running: false }));
};
```

---

### Pattern 3: Progress Modal

```jsx
{batchState.progress.length > 0 && (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
    <div className="bg-[#1E293B] border border-slate-700/50 rounded-xl
                    p-6 w-full max-w-lg mx-4">

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">
          {batchState.running ? 'Sending Reports...' : 'Batch Complete'}
        </h3>
        {!batchState.running && (
          <button onClick={() => setBatchState({ running: false, progress: [], current: 0, total: 0 })}>
            <X className="w-5 h-5 text-slate-400 hover:text-white" />
          </button>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-700 rounded-full h-2 mb-4">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${(batchState.current / batchState.total) * 100}%` }}
        />
      </div>
      <p className="text-sm text-slate-400 mb-4">
        {batchState.current} / {batchState.total}
      </p>

      {/* Item Status List */}
      <div className="max-h-64 overflow-y-auto space-y-2">
        {batchState.progress.map(p => (
          <div key={p.id}
               className="flex items-center justify-between px-3 py-2
                          bg-slate-800/50 rounded-lg">
            <span className="text-sm text-slate-300 truncate">{p.name}</span>
            <span className="flex items-center gap-2 text-xs">
              {p.status === 'pending' && (
                <Circle className="w-3 h-3 text-slate-500" />
              )}
              {p.status === 'sending' && (
                <div className="w-3 h-3 border-2 border-blue-400
                                border-t-transparent rounded-full animate-spin" />
              )}
              {p.status === 'done' && (
                <>
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-green-400">{p.result?.summary}</span>
                </>
              )}
              {p.status === 'error' && (
                <span className="text-red-400">Failed</span>
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  </div>
)}
```

---

## Real-World Example: Batch Forensic Reports

The MERN LMS uses this exact pattern to send forensic timing analysis reports to multiple students:

```javascript
const handleBatchForensic = async () => {
  const allStudents = selectedStudents.size > 0
    ? students.filter(s => selectedStudents.has(s.id))
    : students;

  // ... initialize batchForensic state ...

  for (const s of allStudents) {
    // 1. Fetch student detail (lessons data)
    const detailRes = await getStudentDetail(courseId, s.id);

    // 2. Compute forensic analysis (shared utility)
    const forensic = computeForensicData(detailRes.data?.lessons || []);

    // 3. Build plain-text summary
    const summaryText = buildForensicSummaryText(forensic, s.name, course?.title);

    // 4. Start/get conversation
    const convResult = await startConversation(s.id);

    // 5. Send message
    await sendMessage(convResult.data?.conversationId, { content: summaryText });
  }
};
```

---

## Key Architectural Decisions

### Sequential vs Parallel Processing
**Sequential** is preferred for batch operations because:
- Avoids API rate limits
- Easier to track progress
- One failure doesn't affect others
- Server load stays manageable
- For small batches (10-30 items), speed difference is negligible

### Client-Side vs Server-Side Batch
**Client-side** is appropriate when:
- Batch size is small (< 100 items)
- Each item needs different computation
- Real-time progress feedback is important
- No transactional requirements (each item independent)

**Server-side** is better when:
- Batch size is large (100+ items)
- Need transactional guarantees
- Background processing is acceptable
- Rate limiting is a concern

### Set vs Array for Selection State
**`Set`** is optimal because:
- O(1) `has()` for checkbox checked state
- O(1) `add()` / `delete()` for toggle
- No duplicates possible
- `.size` property for count

---

## Common Mistakes to Avoid

- Do NOT forget `e.stopPropagation()` on checkbox cells when rows are clickable
- Do NOT use `Promise.all()` for batch — sequential prevents rate limits
- Do NOT break on error — continue processing remaining items
- Do NOT close the modal automatically — let users review results
- Do NOT use array index as React key — use item ID
- Do NOT forget the "clear selection" button — users need an escape hatch
- Do NOT hide the progress modal while batch is running — no cancel = bad UX

---

## Testing Checklist

- [ ] Select individual checkboxes — only those students selected
- [ ] Select-all checkbox — all students selected
- [ ] Deselect one after select-all — count updates correctly
- [ ] Clear button — removes all selections
- [ ] Button label shows "(3)" when 3 selected, "to All (23)" when none
- [ ] Batch with selection — only selected students receive messages
- [ ] Batch without selection — all students receive messages
- [ ] Progress bar animates correctly
- [ ] Failed items show error but don't stop batch
- [ ] Modal close button only appears after batch completes
- [ ] Checkbox click doesn't navigate to detail page

---

## Time to Implement

**3-4 hours** for all three patterns combined

## Difficulty Level

### Checkbox Selection: 2/5
### Batch Processing: 3/5
### Progress Modal: 2/5
### Integration (all three): 3/5

---

**Author Notes:**
The `stopPropagation` on checkbox cells was the trickiest part — without it, clicking a checkbox also triggers the row's `onClick` handler, navigating away from the page and losing all state. Always wrap checkbox `<td>` elements with `onClick={(e) => e.stopPropagation()}` when rows have click handlers.

The `Set` approach for tracking selections is much cleaner than the common pattern of toggling array includes/excludes. React's functional state updates (`prev => new Set(prev)`) work perfectly with Sets.
