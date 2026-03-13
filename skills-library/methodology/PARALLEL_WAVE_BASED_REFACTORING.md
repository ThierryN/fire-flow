# Parallel Breath-Based UI Refactoring - Multi-Agent Execution Pattern

## The Problem

Large-scale UI refactoring tasks (migrating pages to new component library, updating styling, etc.) are time-consuming when done sequentially. Refactoring 4 admin pages could take 8-11 hours if done one at a time.

### Why Sequential Refactoring is Slow

- **Context switching** - Mental overhead of moving between pages
- **Repetitive work** - Same patterns applied to different files
- **No parallelization** - One developer (or agent) can only work on one file at a time
- **Fatigue errors** - Quality decreases as work continues

### Impact

- **Time cost:** 2-3 hours per page × 4 pages = 8-12 hours
- **Opportunity cost:** Cannot work on other features during refactoring
- **Risk of inconsistency:** Manual refactoring across many files leads to inconsistent patterns
- **Testing delays:** All work must complete before testing begins

---

## The Solution

### Breath-Based Parallel Execution

Break the work into **breaths** of independent tasks and execute multiple fire-executor agents in parallel for each breath.

**Key Principle:** Independent tasks = Can run in parallel

### How It Works

1. **Identify independent tasks** - Pages that don't depend on each other
2. **Group into breaths** - Each breath contains tasks that can run simultaneously
3. **Launch parallel agents** - One fire-executor per task in the breath
4. **Wait for breath completion** - All agents in breath must finish before next breath
5. **Verify between breaths** - Test each breath before proceeding

### Real-World Example: MERN LMS UI Library Migration

**Goal:** Migrate 4 admin pages to UI component library
- Users.jsx (1,909 lines)
- Products.jsx (1,154 lines)
- Courses.jsx (759 lines)
- LearningPaths.jsx (1,209 lines)

**Traditional Approach:** 8-11 hours (2-3 hours per page)
**Parallel Approach:** 25 minutes total (10 min Breath 1 + 15 min Breath 2)

**Breath Configuration:**
```
Breath 1 (2 agents in parallel):
├─ Agent A: Migrate Users.jsx
└─ Agent B: Migrate Products.jsx

Breath 2 (2 agents in parallel):
├─ Agent C: Migrate Courses.jsx
└─ Agent D: Migrate LearningPaths.jsx
```

**Time Savings:** 96% faster (11 hours → 25 minutes)

---

## Implementation Guide

### Step 1: Create Execution Plan

Document in `.planning/phases/refactoring/R.X-XX-BLUEPRINT.md`:

```markdown
# R.1-01: Component Library Migration

## Tasks
1. Migrate Users.jsx (24 buttons, 1 spinner)
2. Migrate Products.jsx (20 buttons, 7 badges, 1 spinner)
3. Migrate Courses.jsx (13 buttons, status badges, icons)
4. Migrate LearningPaths.jsx (preserve drag-and-drop)

## Breath Breakdown

### Breath 1 (Parallel)
- Task 1: Users.jsx → fire-executor agent
- Task 2: Products.jsx → fire-executor agent

### Breath 2 (Parallel)
- Task 3: Courses.jsx → fire-executor agent
- Task 4: LearningPaths.jsx → fire-executor agent

## Success Criteria
- [ ] All buttons use `<Button>` component
- [ ] All badges use `<Badge>` component
- [ ] All spinners use `<Spinner>` component
- [ ] Production build passes
- [ ] Manual testing confirms functionality
```

### Step 2: Launch Breath 1

Use the Task tool to spawn multiple fire-executor agents **in a single message**:

```javascript
// CRITICAL: All Task calls in ONE message for parallel execution
Task({
  subagent_type: "fire-executor",
  description: "Migrate Users.jsx to UI library",
  prompt: `Migrate client/src/pages/admin/Users.jsx to use UI component library.

Replace all instances of:
- Custom button elements → <Button> from '@/components/ui'
- Loading indicators → <Spinner.Page>
- Custom badges → <Badge>

Preserve all functionality. Test thoroughly.

Import: import { Button, Table, Badge, Spinner, Modal } from '@/components/ui';

Success: Production build passes, no regressions.`
});

Task({
  subagent_type: "fire-executor",
  description: "Migrate Products.jsx to UI library",
  prompt: `Migrate client/src/pages/admin/Products.jsx to use UI component library.

Replace all instances of:
- Custom button elements → <Button> from '@/components/ui'
- Status badges → <Badge variant="...">
- Loading indicators → <Spinner.Page>

Preserve all functionality. Test thoroughly.

Success: Production build passes, no regressions.`
});
```

### Step 3: Monitor Breath Completion

Wait for all agents in the breath to complete. Check their outputs:

```bash
# View agent outputs
ls C:\Users\FirstName\AppData\Local\Temp\claude\c--path-to-my-other-project\tasks\*.output

# Read specific agent output
Read tool: C:\Users\FirstName\AppData\Local\Temp\claude\...\tasks\{agent-id}.output
```

### Step 4: Verify Breath Results

Before launching next breath:

1. **Check git status:**
   ```bash
   git status
   git diff
   ```

2. **Run build:**
   ```bash
   cd client && npm run build
   ```

3. **Manual spot check:**
   - Open one migrated page
   - Verify buttons work
   - Check UI appearance

### Step 5: Launch Next Breath

Repeat Steps 2-4 for Breath 2, Breath 3, etc.

### Step 6: Final Testing

After all breaths complete:

1. **Production build:**
   ```bash
   npm run build
   ```

2. **Dev server testing:**
   ```bash
   npm run dev
   # Test all migrated pages manually
   ```

3. **Create testing checklist:**
   ```markdown
   # Testing Checklist

   ## Users.jsx
   - [ ] Buttons work
   - [ ] Badges display correctly
   - [ ] Spinner shows during load
   - [ ] No console errors

   ## Products.jsx
   - [ ] ... (similar checks)

   ## Courses.jsx
   - [ ] ... (similar checks)

   ## LearningPaths.jsx
   - [ ] Drag-and-drop works
   - [ ] ... (critical features)
   ```

---

## Code Example: Launching Parallel Agents

### ❌ WRONG: Sequential (one at a time)

```javascript
// This runs agents sequentially - SLOW!
Task({ subagent_type: "fire-executor", description: "Task 1", prompt: "..." });
// Wait for response...
Task({ subagent_type: "fire-executor", description: "Task 2", prompt: "..." });
// Wait for response...
```

### ✅ CORRECT: Parallel (all at once)

```javascript
// This runs agents in parallel - FAST!
// SINGLE MESSAGE with multiple Task calls:

Task({ subagent_type: "fire-executor", description: "Task 1", prompt: "..." });
Task({ subagent_type: "fire-executor", description: "Task 2", prompt: "..." });
Task({ subagent_type: "fire-executor", description: "Task 3", prompt: "..." });
Task({ subagent_type: "fire-executor", description: "Task 4", prompt: "..." });

// All 4 agents start simultaneously!
```

---

## When to Use This Pattern

### ✅ Perfect For:

- **UI component migrations** - Multiple pages to same component library
- **Styling updates** - Applying new design system across pages
- **Import path changes** - Updating imports across many files
- **Pattern standardization** - Replacing old patterns with new ones
- **Code modernization** - Updating to new APIs/libraries

### ✅ Requirements:

- Tasks must be **independent** (no dependencies between them)
- Each task has **clear success criteria**
- Work can be **verified in isolation**
- Changes affect **different files** (no merge conflicts)

### ❌ NOT Suitable For:

- **Interdependent tasks** - Task B depends on Task A's output
- **Shared file editing** - Multiple tasks editing same file
- **Complex architectural changes** - Need sequential thinking
- **Unknown scope** - Can't break into independent tasks

---

## Benefits

### Time Savings

| Pages | Sequential | Parallel (2 breaths) | Savings |
|-------|------------|-------------------|---------|
| 4 pages | 8-11 hours | 25 minutes | 96% faster |
| 8 pages | 16-22 hours | 50 minutes | 95% faster |
| 12 pages | 24-33 hours | 75 minutes | 96% faster |

### Quality Improvements

- **Consistency** - All agents follow same prompt/pattern
- **No fatigue** - Fresh context for each agent
- **Parallel review** - Can compare outputs side-by-side
- **Faster feedback** - Discover issues early (after Breath 1)

### Risk Reduction

- **Breath-based verification** - Catch issues before they multiply
- **Isolated failures** - One agent failing doesn't block others
- **Easy rollback** - Can revert individual tasks
- **Clear accountability** - Know which agent did what

---

## Testing the Results

### Build Verification

```bash
# Client build
cd client && npm run build

# Full production build
npm run build
```

**Expected:** No errors, warnings acceptable

### Manual Testing Checklist

For each migrated page:

```markdown
- [ ] Page loads without errors
- [ ] Buttons render correctly
- [ ] Button clicks work
- [ ] Loading states show properly
- [ ] Badges display correct variants
- [ ] Icons render properly
- [ ] No console errors
- [ ] No visual regressions
```

### Critical Feature Testing

For pages with complex features (drag-and-drop, etc.):

```markdown
LearningPaths.jsx:
- [ ] Can open Edit modal
- [ ] Can drag courses to reorder
- [ ] Can remove courses
- [ ] Can add new courses
- [ ] Save button works
- [ ] Modal closes after save
- [ ] Course titles display correctly
```

---

## Common Pitfalls

### ❌ Mistake 1: Dependencies Between Tasks

**Problem:** Task B needs Task A's output
**Solution:** Put them in different breaths (A in Breath 1, B in Breath 2)

### ❌ Mistake 2: Editing Same File

**Problem:** Two agents modify same file = merge conflicts
**Solution:** One agent per file, or different sections if large file

### ❌ Mistake 3: No Verification Between Breaths

**Problem:** Breath 1 breaks build, Breath 2 agents waste time on broken code
**Solution:** Always verify build after each breath

### ❌ Mistake 4: Vague Prompts

**Problem:** Agents implement differently = inconsistent results
**Solution:** Detailed prompts with examples and success criteria

### ❌ Mistake 5: Too Many Breaths

**Problem:** 8 breaths with 1 task each = overhead outweighs benefit
**Solution:** Aim for 2-4 breaths with 2-4 tasks each

---

## Advanced: Breath Optimization

### Optimal Breath Size

| Breath Size | Pros | Cons |
|-----------|------|------|
| 2 tasks/breath | Easy to manage, clear outputs | Not maximizing parallelism |
| 3-4 tasks/breath | **Optimal balance** | Need careful planning |
| 5+ tasks/breath | Maximum speed | Hard to track, higher failure risk |

**Recommendation:** 2-4 tasks per breath for most projects

### Dependency Mapping

Before creating breaths, map dependencies:

```
Task 1 (Users.jsx) → No dependencies
Task 2 (Products.jsx) → No dependencies
Task 3 (Courses.jsx) → Depends on Task 1 (uses same pattern)
Task 4 (LearningPaths.jsx) → No dependencies

Breath Assignment:
Breath 1: Task 1, Task 2, Task 4 (all independent)
Breath 2: Task 3 (uses pattern from Task 1)
```

---

## Related Patterns

- [Breath-Based Parallel Execution](./BREATH_BASED_PARALLEL_EXECUTION.md)
- [Parallel Agent Investigation](./PARALLEL_AGENT_INVESTIGATION.md)
- [Multi-Agent Orchestration](./ADVANCED_ORCHESTRATION_PATTERNS.md)
- [Code Review After Parallel Work](../patterns-standards/PARALLEL_WORK_CODE_REVIEW.md)

---

## Resources

- [Claude Code Task Tool Documentation](https://docs.anthropic.com/claude-code/tools/task)
- [Dominion Flow Plugin](https://github.com/ThierryN/dominion-flow)
- [fire-executor Agent Type](https://docs.anthropic.com/claude-code/agents/fire-executor)

---

## Time to Implement

**Setup:** 15-30 minutes (create plan, identify breaths)
**Execution:** Depends on task complexity, but typically 60-90% faster than sequential

## Difficulty Level

⭐⭐⭐ (3/5) - Requires planning and agent management skills

---

**Author Notes:**

This pattern saved 10+ hours on the MERN LMS UI refactoring (Feb 15, 2026). The key insights:

1. **Plan breaths before launching** - Don't improvise agent spawning
2. **Verify between breaths** - Catch issues early before they multiply
3. **Detailed prompts** - Agents need clear instructions for consistency
4. **Git is your friend** - Commit after each breath for easy rollback

**The magic moment:** Watching 4 agents work simultaneously while you grab coffee ☕

**Pattern Recognition:**
- Whenever you think "this will take hours of repetitive work"
- Ask: "Can I break this into independent tasks?"
- If yes → Parallel breaths
- If no → Find the dependencies and sequence accordingly

This is not just a time saver - it's a workflow transformation.
