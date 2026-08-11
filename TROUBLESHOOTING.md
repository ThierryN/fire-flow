# Dominion Flow Troubleshooting Guide

Common failure modes and their fixes.

---

## 1. Autonomous mode won't stop

**Symptoms:**
- `/fire-autonomous` or `/fire-loop` continues iterating past the point of usefulness
- Agent ignores Sabbath Rest warnings and keeps working
- Iteration count climbing with no meaningful progress

**Likely Cause:**
- `--max-iterations` set too high (default 50)
- `--no-circuit-breaker` flag was passed, disabling the safety net
- Completion promise text doesn't match actual output (e.g., "DONE" vs "Done")

**Fix Steps:**
1. Press `Ctrl+C` to interrupt the current iteration
2. Run `/fire-loop-stop` to formally end the loop and save state
3. Check `.planning/loops/fire-loop-*.md` for the loop state file
4. Review the "Approaches Tried" section to see what was attempted

**Prevention:**
- Use `--max-iterations 20` for most tasks (30 max for complex work)
- Never use `--no-circuit-breaker` unless you're monitoring closely
- Write precise completion promises: `--completion-promise "ALL TESTS PASS"`
- Use `--aggressive` for tighter stall/spin detection thresholds

---

## 2. Wrong files modified

**Symptoms:**
- Files in a different project were edited by a subagent
- Changes landed in the wrong directory
- Cross-project contamination (e.g., editing `my-other-project` instead of `my-project`)

**Likely Cause:**
- Working directory didn't match the project in CONSCIENCE.md
- Subagent resolved a relative path to the wrong project
- Multiple project directories open in the same session

**Fix Steps:**
1. Run `git diff` in the affected project to see what changed
2. Run `git checkout -- .` to revert unwanted changes (or `git stash` to save them)
3. Check CONSCIENCE.md -- does it reference the correct project path?
4. Verify `pwd` matches the expected project root before re-running

**Prevention:**
- The Path Verification Gate (Step 3.5 in `/fire-3-execute`) catches this automatically
- Always use absolute paths when working across multiple projects
- Run `/fire-0-orient` at session start to confirm you're in the right place
- When spawning subagents, the `<path_constraint>` block is injected automatically -- verify it matches

---

## 3. Memory features not working

**Symptoms:**
- Episodic memory injection (Step 7.1 in `/fire-loop`) returns no results
- `/fire-reflect` can't search past reflections
- "Connection refused" errors mentioning port 6335

**Likely Cause:**
- Qdrant is not running (native binary at `C:\path\to\qdrant\qdrant.exe`)
- Qdrant is running but on the wrong port (6333 = Docker backup, 6335 = native primary)
- Ollama embedding service is down (needed for `nomic-embed-text` 768d vectors)

**Fix Steps:**
1. Check Qdrant health: `curl http://localhost:6335/healthz`
2. If down, start it: `C:\path\to\qdrant\qdrant.exe` (runs on port 6335)
3. Check Ollama: `curl http://localhost:11434/api/tags`
4. If Ollama is down: `ollama serve` in a separate terminal
5. Verify the collection exists: `curl http://localhost:6335/collections/power_flow_memory`

**Prevention:**
- Dominion Flow degrades gracefully: if Qdrant is unreachable, it falls back to file-based search across `~/.claude/warrior-handoffs/` and `~/.claude/reflections/`
- The file-based fallback is slower but functional -- memory retrieval is never silently skipped
- Add Qdrant to your system startup if you use memory features regularly

---

## 4. Verification always fails

**Symptoms:**
- `/fire-4-verify` consistently returns REJECTED or CONDITIONAL
- Score stuck below 49 even for seemingly complete work
- E2E (Playwright) category drags the score down on non-UI projects

**Likely Cause:**
- The 70-point checklist includes 10 points for E2E/Playwright testing -- irrelevant for CLI, API-only, or library projects
- Documentation category (10 points) penalizes when README/JSDoc isn't written yet
- Validation thresholds: 63-70 = APPROVED, 56-62 = APPROVED*, 49-55 = CONDITIONAL, <42 = REJECTED

**Fix Steps:**
1. Check `.planning/phases/{N}-{name}/{N}-VERIFICATION.md` for the breakdown
2. Identify which categories are scoring zero
3. For non-UI projects: the E2E category should be redistributed to other categories by the verifier -- if it isn't, note this as a configuration issue
4. Focus on the must-haves first: if all must-haves pass, CONDITIONAL is often acceptable for early phases

**Prevention:**
- Run `/fire-4-verify` with awareness of what the 7 categories are: Code Quality /10, Testing /10, Security /10, Performance /10, Documentation /10, Infrastructure /10, E2E /10
- For API-only projects, tell the verifier in the plan: "No E2E -- redistribute points to Testing and Security"
- Use `/fire-double-check` for a quick sanity check before the full 70-point verification

---

## 5. Plans executed in wrong order

**Symptoms:**
- Breath 2 tasks fail because Breath 1 outputs don't exist yet
- Tasks with dependencies execute before their dependencies complete
- File conflicts between parallel executors

**Likely Cause:**
- `breath:` frontmatter in BLUEPRINT.md files is incorrectly assigned
- `depends_on:` field missing or wrong in the plan files
- Execution mode selected PARALLEL when it should have been SEQUENTIAL (file overlap)

**Fix Steps:**
1. Open `.planning/phases/{N}-{name}/` and check each BLUEPRINT.md frontmatter
2. Verify `breath:` numbers -- all tasks in Breath 1 should have no external dependencies
3. Verify `depends_on:` lists reference only tasks in earlier breaths
4. Re-run `/fire-2-plan {N}` to regenerate plans with correct breath assignment

**Prevention:**
- The planner agent validates breath assignments during `/fire-2-plan`
- `/fire-3-execute` auto-detects file overlap and downgrades from PARALLEL to SEQUENTIAL
- Review the execution manifest at Step 2 before proceeding

---

## 6. Context window filling up fast

**Symptoms:**
- Claude starts forgetting earlier instructions mid-session
- Output quality degrades after 10-15 iterations
- Sabbath Rest triggers repeatedly at low iteration counts

**Likely Cause:**
- Large files loaded into context (reading entire source files instead of relevant sections)
- Skills library injecting too many skills per iteration (max should be 3)
- No `.powerignore` file to exclude noise (node_modules, build artifacts, etc.)

**Fix Steps:**
1. Run `/compact` with a focus topic: `/compact Focus on phase 3 execution`
2. Delegate research tasks to subagents instead of doing them in the main context
3. Create a `.powerignore` file in the project root listing directories to exclude
4. For `/fire-loop`: if iteration > 15, accept the Sabbath Rest and `/fire-loop-resume` in a fresh context

**Prevention:**
- Keep iteration output concise -- the recitation block is capped at 30 lines for a reason
- Use `/fire-search` to find relevant skills BEFORE starting work (don't search mid-loop)
- Read only the relevant sections of large files (use line offsets)
- After 2 failed approaches, `/clear` and restart with the lessons learned

---

## 7. Agent spawns fail

**Symptoms:**
- "Agent definition not found" error when running `/fire-3-execute` or `/fire-7-review`
- Subagent starts but immediately errors out
- SWARM mode fails to create team members

**Likely Cause:**
- Agent definition file missing from `agents/` directory
- Agent file has incorrect frontmatter (missing `name:` or `description:`)
- Agent's `tools:` list references unavailable tools

**Fix Steps:**
1. Check that all agent files exist: `ls ~/.claude/plugins/dominion-flow/agents/`
2. Expected files: `fire-executor.md`, `fire-planner.md`, `fire-researcher.md`, `fire-verifier.md`, `fire-reviewer.md`
3. Verify each file has valid YAML frontmatter with `name:` and `description:`
4. If a file is missing, run `/fire-update` to pull the latest plugin version

**Prevention:**
- Don't manually edit agent files unless you know the frontmatter schema
- After updating the plugin, verify agents: `ls ~/.claude/plugins/dominion-flow/agents/`
- SWARM mode requires the experimental teams flag: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

---

## 8. Skills not found

**Symptoms:**
- `/fire-search` returns no results for queries that should match
- Planner agent says "no relevant skills found" during `/fire-2-plan`
- Skills referenced in plans don't exist at the expected path

**Likely Cause:**
- Skills library path misconfigured or missing
- Project-local skills out of sync with global library
- Skill was deleted or moved to a different category

**Fix Steps:**
1. Check the skills library exists: `ls ~/.claude/plugins/dominion-flow/skills-library/`
2. Run `/fire-skills-sync --pull` to pull latest skills from global to project
3. Run `/fire-skills-sync --dry-run` to see what's out of sync
4. If a specific skill is missing, search by keyword: `/fire-search "{topic}"`

**Prevention:**
- Run `/fire-skills-sync --pull` at the start of each major session
- After contributing a new skill, verify it appears: `/fire-search "{skill name}"`
- Keep skills in their correct category directory -- don't move them manually

---

## 9. Circuit breaker tripped

**Symptoms:**
- Loop stops with "CIRCUIT BREAK" banner
- State shows SPINNING or STALLED or DEGRADED
- Message: "Error seen N times. Previous approaches: {list}"

**Likely Cause:**
- **STALLED:** No file changes for 3+ iterations -- agent is reading/thinking but not acting
- **SPINNING:** Same error hash repeated 4+ times -- agent retrying the same failed approach
- **DEGRADED:** Output volume declining 50%+ from baseline -- context rot setting in

**Fix Steps:**
1. Read the loop state file: `.planning/loops/fire-loop-{ID}.md`
2. Check the "Approaches Tried" section -- these are what NOT to repeat
3. For STALLED: the fix is usually to try a fundamentally different approach
4. For SPINNING: read the error carefully -- the repeated error hash tells you exactly what's failing
5. For DEGRADED: accept the Sabbath Rest, `/clear`, then `/fire-loop-resume {ID}`

**Prevention:**
- Use `--aggressive` for tasks where you expect quick resolution (tighter thresholds)
- Write clear completion criteria so the loop knows when it's done
- Trust the circuit breaker -- forcing through a tripped breaker wastes iterations
- After a trip, always read the loop file before resuming to understand what was tried

---

## 10. Handoff incomplete

**Symptoms:**
- `/fire-6-resume` can't find a handoff file or shows stale data
- Handoff missing key sections (blockers, in-progress work, skills applied)
- Next session agent doesn't have enough context to continue

**Likely Cause:**
- `/fire-5-handoff` wasn't run before ending the session
- Handoff was created but CONSCIENCE.md was out of date at the time
- Session ended abruptly (crash, Ctrl+C) before handoff could complete

**Fix Steps:**
1. Run `/fire-5-handoff` manually to create a fresh handoff from current state
2. Check `.planning/` for any `POWER-HANDOFF-*.md` files -- there may be a partial one
3. If CONSCIENCE.md is stale, update it manually with current phase status
4. Verify the handoff follows WARRIOR 7-step format: What / Accomplished / Remaining / Resources / Issues / Observations / Recommendations

**Prevention:**
- Always run `/fire-5-handoff` before ending a session -- make it a habit
- The `stop-verify.js` hook warns if tasks are incomplete when you exit
- For long sessions, create intermediate handoffs every 2-3 hours
- If using `/fire-loop`, the Sabbath Rest snapshot serves as an automatic partial handoff

---

*If your issue isn't listed here, check the references directory for detailed protocol documentation, or run `/fire-debug` to systematically investigate.*
