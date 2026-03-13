# PM2 Memory Exhaustion - Node.js Heap Size Fix for Production

## The Problem

Production server experiencing **constant restarts** (4-5 per hour) with email alerts showing brief downtimes of a few seconds. Server appears to crash and auto-restart continuously.

### Symptoms
```
PM2 Status:
- Restarts: 53 in 12 hours
- Uptime: Resets every hour
- Heap Usage: 94.54% (137 MB / 145 MB)
- HTTP P95 Latency: 25 seconds (should be <1s)
- Status: Online but unstable
```

### Why It Was Hard

- **Silent failure** - No crash stack traces, only brief downtime alerts
- **Auto-restart masks problem** - PM2 keeps restarting so users don't notice long outages
- **Looks like code errors** - Initial assumption was application bugs causing crashes
- **Memory limit not obvious** - Node.js default heap size (~145MB) is invisible in PM2 status
- **Normal errors in logs** - 404s, CORS, auth failures distract from real issue

### Impact

- **User experience** - Intermittent errors during restart windows
- **Operations cost** - Constant email alerts (dozens per day)
- **Reliability perception** - "Is the site down?" questions from users
- **Debugging time wasted** - Investigating wrong problems (code errors vs infrastructure)

---

## The Solution

**Root Cause:** Node.js default heap size (~145 MB) is too small for the application's memory footprint under production load.

### Diagnosis Commands

```bash
# Check PM2 status and restart count
ssh user@server "pm2 info APP_NAME | grep -E '(restarts|heap|memory)'"

# Check heap usage
ssh user@server "pm2 info APP_NAME"
# Look for:
# - Heap Usage > 90% = CRITICAL
# - Restarts > 10/day = PROBLEM
# - Used Heap Size approaching limit

# Check Node.js heap limit (if configured)
ssh user@server "ps aux | grep node"
# Look for --max-old-space-size flag
```

### The Fix: Create PM2 Ecosystem Config

Create `ecosystem.config.js` in project root:

```javascript
module.exports = {
  apps: [{
    name: 'LMS-SERVER',
    script: './server/server.js',
    cwd: '/home/user/app-directory',
    instances: 1,
    exec_mode: 'fork',

    // CRITICAL: Memory management
    max_memory_restart: '450M',  // Restart before OOM (before 512M limit)
    node_args: '--max-old-space-size=512',  // 512MB heap (vs default ~145MB)

    // Restart policy
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',

    // Logging
    error_file: '/home/user/.pm2/logs/APP-error.log',
    out_file: '/home/user/.pm2/logs/APP-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

    // Environment
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
};
```

### Apply the Configuration

```bash
# SSH into server
ssh user@server

# Navigate to app directory
cd ~/app-directory

# Stop current PM2 process
pm2 delete APP_NAME

# Start with new configuration
pm2 start ecosystem.config.js

# Save PM2 configuration (persist across reboots)
pm2 save

# Verify new heap size
pm2 info APP_NAME | grep "interpreter args"
# Should show: --max-old-space-size=512
```

### Memory Sizing Guidelines

| Server RAM | Recommended Heap Size | Notes |
|------------|----------------------|-------|
| 512 MB | 256 MB | Minimal setup |
| 1 GB | 512 MB | Small to medium apps |
| 2 GB | 1 GB | Medium apps |
| 4+ GB | 1.5-2 GB | Large apps |

**Rule of Thumb:** Set heap to **40-50% of available server RAM** if running single process.

### Choosing max_memory_restart Value

Set `max_memory_restart` to **~90% of heap size**:
- Heap 512 MB → restart at 450 MB
- Heap 1 GB → restart at 900 MB
- Heap 2 GB → restart at 1800 MB

This allows graceful restart before OOM crash.

---

## Testing the Fix

### Before
```bash
pm2 info LMS-SERVER
# Heap Usage: 94.54%
# Restarts: 53 (in 12 hours)
# HTTP P95 Latency: 25000 ms
```

### After
```bash
pm2 info LMS-SERVER
# Heap Usage: 42% (218 MB / 512 MB)
# Restarts: 0
# HTTP P95 Latency: <100 ms
```

### Monitor Over 24 Hours

```bash
# Check restart count
ssh user@server "pm2 info APP_NAME | grep restarts"

# Monitor memory usage live
ssh user@server "pm2 monit"

# Check logs for OOM errors
ssh user@server "pm2 logs APP_NAME --err --lines 100 | grep -i 'memory\|heap\|allocation'"
```

**Success Criteria:**
- Restart count stays at 0 or low (<5 per day)
- Heap usage stays below 80%
- No email alerts for downtime
- Response times improve

---

## Prevention

### 1. Always Configure PM2 with Ecosystem File

**Never run PM2 without heap size configuration in production.**

```bash
# ❌ WRONG - Uses Node.js defaults
pm2 start server.js --name APP_NAME

# ✅ CORRECT - Uses explicit heap size
pm2 start ecosystem.config.js
```

### 2. Monitor Memory in Staging

Test memory usage in staging before production:

```bash
# Load test in staging
npm install -g artillery
artillery quick --count 100 --num 10 https://staging.example.com

# Watch memory during load test
pm2 monit
```

### 3. Set Up Alerts

Configure PM2 to alert BEFORE memory exhaustion:

```javascript
// In ecosystem.config.js
max_memory_restart: '450M',  // Restart at 450MB
// Also set up external monitoring (New Relic, Datadog, etc.)
```

### 4. Check for Memory Leaks

If memory grows over time even with larger heap:

```bash
# Take heap snapshot
pm2 trigger APP_NAME km:heapdump

# Analyze in Chrome DevTools
# Look for: setInterval not cleared, event listeners accumulating, large caches
```

### 5. Deployment Checklist

Before deploying new code:

- [ ] Check for `setInterval`/`setTimeout` without cleanup
- [ ] Verify event listeners are removed
- [ ] Check for unbounded caches (Map, Set without size limits)
- [ ] Test memory usage in staging under load
- [ ] Verify `ecosystem.config.js` is committed and deployed

---

## Common Mistakes to Avoid

- ❌ **Ignoring heap usage %** - "94% is fine, right?" NO - that's critical
- ❌ **Assuming code is crashing** - No stack trace = likely memory issue
- ❌ **Setting heap too low** - "256MB should be enough" - test under load first
- ❌ **Not using ecosystem config** - PM2 CLI flags don't persist across restarts
- ❌ **Ignoring restart count** - "PM2 handles it" - but investigate WHY
- ❌ **Setting heap = total RAM** - Leave room for OS and other processes

---

## Related Patterns

- [Node.js Memory Management Best Practices](../patterns-standards/NODEJS_MEMORY_MANAGEMENT.md)
- [PM2 Production Configuration Guide](../deployment-security/PM2_PRODUCTION_CONFIG.md)
- [Memory Leak Detection and Prevention](../patterns-standards/MEMORY_LEAK_DETECTION.md)

---

## Resources

- [Node.js Memory Management](https://nodejs.org/en/docs/guides/simple-profiling/)
- [PM2 Ecosystem File Reference](https://pm2.keymetrics.io/docs/usage/application-declaration/)
- [V8 Heap Size Configuration](https://nodejs.org/api/cli.html#--max-old-space-sizesize-in-megabytes)
- [PM2 Memory Restart](https://pm2.keymetrics.io/docs/usage/process-management/#max-memory-restart)

---

## Time to Implement

**15 minutes** - Create config, restart PM2, verify

## Difficulty Level

⭐⭐ (2/5) - Simple fix once you know the root cause, but diagnosis can be tricky

---

## Real-World Example: MERN Community LMS

**Date:** February 5, 2026
**Server:** schooloftheprophets.club (cPanel shared hosting)
**Problem:** 53 restarts in 12 hours, 94.54% heap usage

**Solution Applied:**
```javascript
// ecosystem.config.js
node_args: '--max-old-space-size=512'  // 512MB heap
max_memory_restart: '450M'
```

**Results:**
- Restarts dropped to 0
- Heap usage: 42% (healthy)
- Email alerts stopped
- Site stability restored

**Server specs:**
- Total RAM: 11 GB
- Node.js: 18.20.8
- Previous heap: ~145 MB (default)
- New heap: 512 MB (3.5x increase)

---

## When This Fix Isn't Enough

If you still see memory growth after increasing heap size, you likely have a **memory leak**:

### Investigation Steps

1. **Identify leak sources:**
   ```bash
   # Check for unclosed intervals
   grep -r 'setInterval' --include='*.js' | grep -v 'clearInterval'

   # Check for event listeners
   grep -r '\.on(' --include='*.js' | grep -v '\.off('
   ```

2. **Take heap snapshots:**
   ```bash
   pm2 trigger APP_NAME km:heapdump
   # Analyze in Chrome DevTools Memory Profiler
   ```

3. **Common leak sources:**
   - WebSocket connections not closed
   - Database connections not released
   - File streams not closed
   - Event listeners accumulating
   - Caches growing unbounded
   - Timers (setInterval) not cleared

4. **Fix patterns:**
   ```javascript
   // ❌ Memory leak
   setInterval(() => { /* ... */ }, 1000);

   // ✅ Proper cleanup
   const interval = setInterval(() => { /* ... */ }, 1000);
   process.on('SIGTERM', () => clearInterval(interval));

   // ❌ Memory leak
   const cache = new Map();
   cache.set(key, value); // Grows forever

   // ✅ Size-limited cache
   const cache = new Map();
   if (cache.size > 1000) {
     const firstKey = cache.keys().next().value;
     cache.delete(firstKey);
   }
   cache.set(key, value);
   ```

---

## Author Notes

This took 30 minutes to diagnose after receiving email alerts about constant restarts. The key insight was recognizing that:

1. **No stack traces = not a code crash** - Memory exhaustion
2. **High heap % + restarts = undersized heap** - Not a leak
3. **PM2 auto-restart = masks the problem** - Seems "fine" but isn't

The fix was trivial (add ecosystem config), but diagnosis required understanding Node.js memory management and PM2 behavior.

**Critical lesson:** Always check heap usage % FGTAT when investigating production instability. It's often the simplest explanation.

---

**Last Updated:** February 5, 2026
**Tested On:** Node.js 18.20.8, PM2 5.x, cPanel shared hosting
