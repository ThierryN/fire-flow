---
description: Check for and apply plugin updates from GitHub repository
---

# /fire-update

> Check for plugin updates, view changelog, and apply updates from GitHub

---

## Purpose

Automatic update system for Dominion Flow plugin that pulls updates from GitHub, maintains version history, and creates backups before updating. Ensures you always have the latest features and fixes.

**Commands:**
- `/fire-update check` - Check for available updates
- `/fire-update apply` - Apply available updates
- `/fire-update history` - View update history
- `/fire-update version` - Show current version
- `/fire-update rollback` - Rollback to previous version

---

## Arguments

```yaml
arguments:
  action:
    required: false
    type: string
    enum: [check, apply, history, version, rollback]
    default: check
    description: "Update action to perform"

  force:
    required: false
    type: boolean
    default: false
    description: "Force update even if on modified branch"

examples:
  - "/fire-update" - Check for available updates
  - "/fire-update check" - Check for updates with details
  - "/fire-update apply" - Apply available updates
  - "/fire-update history" - View update history
  - "/fire-update rollback" - Rollback to previous version
```

---

## Configuration

### GitHub Repository Setup

The plugin must have a GitHub repository configured in `plugin.json`:

```json
{
  "repository": "https://github.com/username/fire-flow"
}
```

If repository is not configured:
```
⚠️  No repository configured for updates

To enable updates, add repository URL to plugin.json:
{
  "repository": "https://github.com/username/fire-flow"
}
```

---

## Process: Check for Updates

### Step 1: Validate Environment

```bash
PLUGIN_DIR="$HOME/.claude/plugins/fire-flow"
VERSION_FILE="$PLUGIN_DIR/version.json"
PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
```

Verify plugin directory exists and is a git repository:

```bash
cd "$PLUGIN_DIR"
if [ ! -d ".git" ]; then
  echo "Error: Not a git repository"
  exit 1
fi
```

### Step 2: Load Current Version

Read `version.json` or create if missing:

```bash
if [ ! -f "$VERSION_FILE" ]; then
  # Initialize version file
  CURRENT_COMMIT=$(git rev-parse HEAD)
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_JSON")

  cat > "$VERSION_FILE" <<EOF
{
  "version": "$PLUGIN_VERSION",
  "commit": "$CURRENT_COMMIT",
  "branch": "$CURRENT_BRANCH",
  "updatedAt": "$(date -Iseconds)",
  "installMethod": "manual"
}
EOF
fi
```

### Step 3: Fetch and Compare

```bash
git fetch origin --quiet 2>&1
REMOTE_COMMIT=$(git rev-parse origin/main 2>/dev/null)
BEHIND_COUNT=$(git rev-list --count HEAD..origin/main)
```

### Step 4: Display Results

**If updates available:**

```
🔄 Updates Available for Dominion Flow

Current Version: 3.0.0 (abc1234)
Remote Version: 3.1.0 (def5678)
Updates: 5 commits behind

Recent Changes:
  • Add pattern discovery integration (def5678)
  • Fix todo duplicate detection (cde4567)
  • Improve verification reporting (bcd3456)

---

To apply updates: /fire-update apply
```

---

## Process: Apply Updates

### Step 1: Create Backup

```bash
BACKUP_DIR="$PLUGIN_DIR/.update-backups"
TIMESTAMP=$(date "+%Y-%m-%dT%H-%M-%S")
BACKUP_NAME="pre-update-$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

mkdir -p "$BACKUP_PATH"

# Store current commit info
cat > "$BACKUP_PATH/backup-info.json" <<EOF
{
  "commit": "$(git rev-parse HEAD)",
  "branch": "$(git rev-parse --abbrev-ref HEAD)",
  "version": "$(jq -r '.version' $VERSION_FILE)",
  "createdAt": "$(date -Iseconds)",
  "label": "pre-update"
}
EOF

# Stash any uncommitted changes
git stash push -m "Update backup $BACKUP_NAME" 2>/dev/null || true
```

### Step 2: Pull Updates

```bash
CURRENT_COMMIT=$(git rev-parse HEAD)
git pull origin main

NEW_COMMIT=$(git rev-parse HEAD)
PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_JSON")
```

### Step 3: Update Version File

```bash
jq --arg commit "$NEW_COMMIT" \
   --arg version "$PLUGIN_VERSION" \
   --arg updated "$(date -Iseconds)" \
   '.commit = $commit | .version = $version | .updatedAt = $updated' \
   "$VERSION_FILE" > "$VERSION_FILE.tmp" && mv "$VERSION_FILE.tmp" "$VERSION_FILE"
```

### Step 4: Record History

```bash
HISTORY_FILE="$PLUGIN_DIR/.update-history.json"

HISTORY_ENTRY=$(cat <<EOF
{
  "type": "update",
  "beforeCommit": "$CURRENT_COMMIT",
  "afterCommit": "$NEW_COMMIT",
  "backup": "$BACKUP_NAME",
  "timestamp": "$(date -Iseconds)"
}
EOF
)

# Prepend to history (keep last 50)
if [ -f "$HISTORY_FILE" ]; then
  jq --argjson entry "$HISTORY_ENTRY" '. = [$entry] + . | .[0:50]' "$HISTORY_FILE" > "$HISTORY_FILE.tmp"
  mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
else
  echo "[$HISTORY_ENTRY]" > "$HISTORY_FILE"
fi
```

### Step 5: Display Success

```
✓ Dominion Flow Updated Successfully

Previous Version: 3.0.0 (abc1234)
New Version: 3.1.0 (def5678)

Changes Applied:
  • 5 commits pulled
  • 23 files changed
  • Backup created: pre-update-2026-02-09T15-30-00

---

🎉 Update complete! New features are now available.

To rollback: /fire-update rollback
```

---

## Process: View History

```bash
HISTORY_FILE="$PLUGIN_DIR/.update-history.json"

jq -r '.[] | "\(.timestamp)|\(.type)|\(.beforeCommit[0:7])|\(.afterCommit[0:7])"' \
  "$HISTORY_FILE" | while IFS='|' read timestamp type before after; do

  DATE=$(date -d "$timestamp" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "$timestamp")

  case "$type" in
    update)
      echo "📦 $DATE: Update ($before → $after)"
      ;;
    rollback)
      echo "↩️  $DATE: Rollback ($before → $after)"
      ;;
  esac
done
```

---

## Process: Rollback

List available backups and restore to selected version:

```bash
BACKUP_DIR="$PLUGIN_DIR/.update-backups"
ls -t "$BACKUP_DIR" | head -n 5

# After user selects backup:
BACKUP_INFO="$BACKUP_DIR/$SELECTED/backup-info.json"
TARGET_COMMIT=$(jq -r '.commit' "$BACKUP_INFO")

# Create pre-rollback backup
# Reset to target commit
git reset --hard "$TARGET_COMMIT"

# Update version.json
```

---

## Success Criteria

- [ ] Current version loaded from version.json
- [ ] Remote repository fetched successfully
- [ ] Updates displayed with commit messages
- [ ] Backups created before applying updates
- [ ] Version file updated after changes
- [ ] Update history recorded

---

## GitHub Token Setup (Private Repositories)

```bash
# Generate token at: https://github.com/settings/tokens
# Set token in git remote
cd ~/.claude/plugins/fire-flow
git remote set-url origin https://YOUR_TOKEN@github.com/username/fire-flow.git
```

---

## References

- **Related:** `/fire-dashboard` - View current plugin version
- **Related:** `plugin.json` - Plugin metadata
