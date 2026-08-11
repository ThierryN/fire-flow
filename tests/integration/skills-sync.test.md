# Integration Test: Skills Sync - Bidirectional Synchronization

## Test Name
`skills-sync-bidirectional`

## Description
Validates that skills can be synchronized bidirectionally between the Dominion Flow plugin's local skills library and the global WARRIOR workflow skills library. Tests both push (contribute) and pull (sync from global) operations.

---

## Prerequisites
- Dominion Flow plugin installed at `~/.claude/plugins/dominion-flow/`
- WARRIOR workflow plugin installed at `~/.claude/plugins/warrior-workflow/`
- Both plugins have skills-library directories
- Write permissions to both directories

---

## Setup Steps

```bash
# 1. Define paths
DOMINION FLOW_SKILLS="$HOME/.claude/plugins/dominion-flow/skills-library"
WARRIOR_SKILLS="$HOME/.claude/plugins/warrior-workflow/skills-library"

# 2. Verify both directories exist
[ -d "$DOMINION FLOW_SKILLS" ] && echo "Dominion Flow skills: exists" || echo "Dominion Flow skills: MISSING"
[ -d "$WARRIOR_SKILLS" ] && echo "WARRIOR skills: exists" || echo "WARRIOR skills: MISSING"

# 3. Count existing skills
PF_COUNT=$(find "$DOMINION FLOW_SKILLS" -name "*.md" -type f 2>/dev/null | wc -l)
WF_COUNT=$(find "$WARRIOR_SKILLS" -name "*.md" -type f 2>/dev/null | wc -l)
echo "Dominion Flow skills: $PF_COUNT"
echo "WARRIOR skills: $WF_COUNT"

# 4. Create test skill in WARRIOR (to test pull)
mkdir -p "$WARRIOR_SKILLS/test-category"
cat > "$WARRIOR_SKILLS/test-category/sync-test-skill.md" << 'EOF'
# Sync Test Skill

## Overview
Test skill for validating bidirectional sync functionality.

## Keywords
test, sync, validation

## When to Use
- Testing sync operations
- Validating skill transfer

## Steps
1. This is step one
2. This is step two

## Created By
Integration test - sync-test
EOF

# 5. Create test skill in Dominion Flow (to test push)
mkdir -p "$DOMINION FLOW_SKILLS/test-category"
cat > "$DOMINION FLOW_SKILLS/test-category/dominion-flow-test.md" << 'EOF'
# Dominion Flow Test Skill

## Overview
Test skill created in Dominion Flow for push testing.

## Keywords
powerflow, test, push

## When to Use
- Testing push to global
- Validating contribution

## Steps
1. Dominion Flow step one
2. Dominion Flow step two

## Created By
Integration test - dominion-flow
EOF
```

---

## Execute Steps

### Test Case 1: Pull from Global (WARRIOR -> Dominion Flow)
```bash
# In Claude Code session:
/fire-sync --pull

# Expected behavior:
#   - Scan WARRIOR skills library
#   - Identify skills not in Dominion Flow
#   - Copy new skills to Dominion Flow
#   - Report synced files

# Or if using specific skill:
/fire-sync --pull test-category/sync-test-skill.md
```

### Test Case 2: Push to Global (Dominion Flow -> WARRIOR)
```bash
# In Claude Code session:
/fire-sync --push

# Expected behavior:
#   - Scan Dominion Flow skills library
#   - Identify skills not in WARRIOR
#   - Copy new skills to WARRIOR
#   - Report synced files

# Or if using specific skill:
/fire-sync --push test-category/dominion-flow-test.md
```

### Test Case 3: Bidirectional Sync
```bash
# In Claude Code session:
/fire-sync --all

# Expected behavior:
#   - Pull new skills from WARRIOR
#   - Push new skills to WARRIOR
#   - Skip duplicates
#   - Report all operations
```

### Test Case 4: Conflict Detection
```bash
# Create conflicting skill (same name, different content)
cat > "$DOMINION FLOW_SKILLS/test-category/conflict-skill.md" << 'EOF'
# Conflict Skill - Dominion Flow Version
Content from Dominion Flow
EOF

cat > "$WARRIOR_SKILLS/test-category/conflict-skill.md" << 'EOF'
# Conflict Skill - WARRIOR Version
Content from WARRIOR
EOF

# In Claude Code session:
/fire-sync --all

# Expected behavior:
#   - Detect conflict
#   - Report conflict (don't overwrite automatically)
#   - Offer resolution options
```

---

## Verify Steps

### Pull Verification
```bash
# Check skill was pulled to Dominion Flow
PULLED_SKILL="$DOMINION FLOW_SKILLS/test-category/sync-test-skill.md"
[ -f "$PULLED_SKILL" ] && echo "PASS: Skill pulled to Dominion Flow" || echo "FAIL: Skill not pulled"

# Verify content matches source
if [ -f "$PULLED_SKILL" ]; then
    diff "$PULLED_SKILL" "$WARRIOR_SKILLS/test-category/sync-test-skill.md" > /dev/null
    [ $? -eq 0 ] && echo "PASS: Content matches" || echo "FAIL: Content differs"
fi
```

### Push Verification
```bash
# Check skill was pushed to WARRIOR
PUSHED_SKILL="$WARRIOR_SKILLS/test-category/dominion-flow-test.md"
[ -f "$PUSHED_SKILL" ] && echo "PASS: Skill pushed to WARRIOR" || echo "FAIL: Skill not pushed"

# Verify content matches source
if [ -f "$PUSHED_SKILL" ]; then
    diff "$PUSHED_SKILL" "$DOMINION FLOW_SKILLS/test-category/dominion-flow-test.md" > /dev/null
    [ $? -eq 0 ] && echo "PASS: Content matches" || echo "FAIL: Content differs"
fi
```

### Category Preservation
```bash
# Verify category directories are preserved
[ -d "$DOMINION FLOW_SKILLS/test-category" ] && echo "PASS: PF category preserved" || echo "FAIL: PF category missing"
[ -d "$WARRIOR_SKILLS/test-category" ] && echo "PASS: WF category preserved" || echo "FAIL: WF category missing"
```

### Duplicate Prevention
```bash
# Run sync again - should not duplicate
BEFORE_COUNT=$(find "$DOMINION FLOW_SKILLS" -name "*.md" -type f | wc -l)

# Sync again (in Claude Code):
# /fire-sync --all

AFTER_COUNT=$(find "$DOMINION FLOW_SKILLS" -name "*.md" -type f | wc -l)
[ "$BEFORE_COUNT" -eq "$AFTER_COUNT" ] && echo "PASS: No duplicates" || echo "FAIL: Duplicates created"
```

### Conflict Reporting
```bash
# Check if conflict was reported
# (This is verified through Claude Code output)
echo "Verify Claude Code reported conflict for 'conflict-skill.md'"
```

---

## Cleanup Steps

```bash
# Remove test skills from both locations
rm -f "$DOMINION FLOW_SKILLS/test-category/sync-test-skill.md"
rm -f "$DOMINION FLOW_SKILLS/test-category/dominion-flow-test.md"
rm -f "$DOMINION FLOW_SKILLS/test-category/conflict-skill.md"
rm -f "$WARRIOR_SKILLS/test-category/sync-test-skill.md"
rm -f "$WARRIOR_SKILLS/test-category/dominion-flow-test.md"
rm -f "$WARRIOR_SKILLS/test-category/conflict-skill.md"

# Remove test category if empty
rmdir "$DOMINION FLOW_SKILLS/test-category" 2>/dev/null
rmdir "$WARRIOR_SKILLS/test-category" 2>/dev/null

echo "Cleanup complete"
```

---

## Pass/Fail Criteria

| Criterion | Required | Description |
|-----------|----------|-------------|
| Pull copies new skills | YES | Skills from WARRIOR appear in Dominion Flow |
| Push copies new skills | YES | Skills from Dominion Flow appear in WARRIOR |
| Content preserved | YES | File content identical after sync |
| Categories preserved | YES | Directory structure maintained |
| No duplicates | YES | Re-sync doesn't create copies |
| Conflicts detected | YES | Same-name different-content flagged |
| Conflicts not auto-overwritten | YES | User choice required |
| Sync report generated | NO | Summary of operations shown |

## Expected Result
**PASS** if all required criteria are met.

---

## Sync Strategy Notes

### File Comparison Methods
1. **Filename-based**: Same filename = same skill (fast, may miss renames)
2. **Content hash**: SHA256 of content (accurate, slower)
3. **Metadata-based**: Use skill headers/keywords (semantic, complex)

### Conflict Resolution Options
1. **Keep local**: Prefer Dominion Flow version
2. **Keep remote**: Prefer WARRIOR version
3. **Keep both**: Rename one with suffix
4. **Merge**: Manual merge (for advanced users)

### Recommended Sync Flow
```
1. Pull from WARRIOR (get latest global skills)
2. Review new skills
3. Contribute local skills with /fire-contribute
4. Push to WARRIOR (share with global)
```

---

## Test Variations

### Variation A: Empty Source
- Source has no skills
- Should complete without error
- Report "No new skills to sync"

### Variation B: Large Skill Library
- 100+ skills in source
- Should handle efficiently
- Progress indication shown

### Variation C: Nested Categories
- Skills in deeply nested directories
- Should preserve full path structure

### Variation D: Binary Files Present
- Non-markdown files in skills directory
- Should skip or warn (not sync)

---

## Known Issues
- Symlinks may cause issues (recommend avoiding)
- Very large files may slow sync
- Network-based skills (if any) not supported

## Related Tests
- `skills-search.test.md` - Finding synced skills
- `skills-contribute.test.md` - Creating skills for sync
- `full-workflow.test.md` - Skills used in planning
