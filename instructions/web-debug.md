# Web Application Debugging Guide

## Overview

This guide provides a systematic approach to debugging web applications using the router framework. It demonstrates how to test, identify issues, and fix problems using the available tools with background logging.

## 🔧 Web Debug Flow

### Step 1: Prepare Logging Environment

**CRITICAL: Clean up old logs and prepare logging directory!**

```bash
cd /path/to/your/app

# Remove old logs to start fresh
rm -rf .log
mkdir -p .log

# FIRST: Check if server is already running
ps aux | grep "bun.*$(basename $(pwd))" | grep -v grep

# If server is running, kill it first
pkill -f "bun.*$(basename $(pwd))" || lsof -ti:3000 | xargs kill -9 2>/dev/null || true
```

### Step 2: Start Development Server in Background

**Start the development server in background with comprehensive logging:**

```bash
# Start development server in background with full logging
bun dev > .log/dev-server.log 2>&1 &

# Store the process ID for later management
echo $! > .log/dev-server.pid

# Wait for server to start (check logs)
sleep 3
echo "Server starting... checking logs:"
tail -f .log/dev-server.log &
TAIL_PID=$!
sleep 2
kill $TAIL_PID 2>/dev/null || true
```

### Step 3: Monitor Server Status

**Verify server is running and check for startup errors:**

```bash
# Check if server process is still running
if ps -p $(cat .log/dev-server.pid 2>/dev/null) > /dev/null 2>&1; then
    echo "✅ Server is running (PID: $(cat .log/dev-server.pid))"
else
    echo "❌ Server failed to start. Check logs:"
    cat .log/dev-server.log
    exit 1
fi

# Quick log check for immediate errors
if grep -i "error\|exception\|failed" .log/dev-server.log; then
    echo "⚠️  Errors detected in startup logs"
fi
```

### Step 4: Test with WebFetch Tool

Use the `webfetch` tool to access your application and inspect the generated HTML:

```bash
# Test the main page
webfetch http://localhost:3000 --format html
```

This will show you:

- The actual HTML being generated
- CSS styles being applied
- Any JavaScript being loaded
- Server-side rendering output

### Step 5: Analyze WebFetch Output and Check Logs

**If webfetch returns a 500 error or unexpected output:**

### Step 6: Check Server Logs for Errors

**CRITICAL: Always check dev server logs in .log folder for detailed error information!**

```bash
# Check for 500 errors and other issues in logs
echo "🔍 Checking for errors in server logs..."

# Look for HTTP 500 errors
grep -n "500\|Internal Server Error" .log/dev-server.log

# Look for common error patterns
grep -n -i "error\|exception\|failed\|cannot\|undefined" .log/dev-server.log

# Show recent log entries (last 20 lines)
echo "📋 Recent log entries:"
tail -20 .log/dev-server.log

# Monitor logs in real-time if needed
echo "📺 To monitor logs in real-time, run:"
echo "tail -f .log/dev-server.log"
```

**Look for these specific error patterns in the logs:**

- **HTTP 500 errors** - Server-side rendering failures
- **TypeScript compilation errors** - TS2307, TS2345, etc.
- **Runtime exceptions** - TypeError, ReferenceError, etc.
- **Import/export resolution failures** - Cannot resolve module
- **Theme resolution issues** - Theme property access errors

```bash
# Common error patterns to search for:
# grep "TypeError.*Cannot read property" .log/dev-server.log
# grep "ReferenceError.*not defined" .log/dev-server.log
# grep "SyntaxError.*Unexpected token" .log/dev-server.log
# grep "Error.*Cannot resolve module" .log/dev-server.log
# grep "TS[0-9].*Cannot find module" .log/dev-server.log
```

**Only after checking server logs should you search the codebase for the specific error mentioned in the logs.**

### Step 7: Incremental Debugging with Log Monitoring

When fixing issues, make small changes and monitor logs:

1. **Make minimal change** (e.g., fix one CSS property)
2. **Monitor logs** for immediate feedback: `tail -f .log/dev-server.log`
3. **Test immediately** with webfetch
4. **Check logs again** for any new errors
5. **Verify the change** in HTML output
6. **Continue to next issue**

This prevents breaking multiple things at once and provides real-time feedback.

## 🛠️ Essential Debug Commands

### Server Management with Background Logging

```bash
# Clean up old logs and prepare environment
rm -rf .log && mkdir -p .log

# ALWAYS check first before starting server
ps aux | grep "bun.*your-app" | grep -v grep

# Kill existing server if found (REQUIRED before starting new one)
pkill -f "bun.*your-app" || lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start development server in background with logging
bun dev > .log/dev-server.log 2>&1 &
echo $! > .log/dev-server.pid

# Check server status
ps -p $(cat .log/dev-server.pid) && echo "✅ Server running" || echo "❌ Server failed"

# Stop background server when done
kill $(cat .log/dev-server.pid 2>/dev/null) 2>/dev/null || true
rm -f .log/dev-server.pid
```

### Log Management

```bash
# Monitor logs in real-time
tail -f .log/dev-server.log

# Search for specific errors
grep -i "500\|error\|exception" .log/dev-server.log

# Show recent errors with line numbers
grep -n -i "error" .log/dev-server.log | tail -10

# Clear logs and restart server
kill $(cat .log/dev-server.pid 2>/dev/null) 2>/dev/null || true
rm -rf .log && mkdir -p .log
bun dev > .log/dev-server.log 2>&1 &
echo $! > .log/dev-server.pid
```

### Testing Commands

```bash
# Test main page
webfetch http://localhost:3000 --format html

# Test specific routes
webfetch http://localhost:3000/contacts --format html

# Test with different formats
webfetch http://localhost:3000 --format text
webfetch http://localhost:3000 --format markdown
```

### Code Quality Checks

```bash
# TypeScript compilation
bun run check

# Type checking only
bun run typecheck

# Linting only
bun run biome:check
```

## 📋 Debug Checklist

When debugging web applications, follow this checklist:

### ✅ Pre-Debug Setup

- [ ] Old logs removed from `.log` folder
- [ ] Development server is running in background
- [ ] Server logs are being captured in `.log/dev-server.log`
- [ ] No TypeScript compilation errors in logs
- [ ] All imports are resolved correctly
- [ ] No 500 errors in initial server startup logs

### ✅ HTML Output Analysis

- [ ] Page loads without errors
- [ ] Expected content is present
- [ ] CSS styles are applied correctly
- [ ] No CSS variables in output (use actual values)
- [ ] All elements have `data-debug-id` attributes

### ✅ Performance Checks

- [ ] No JavaScript errors in console
- [ ] Hot reload is working
- [ ] Asset loading is successful
- [ ] WebSocket connection is established

## 🎯 Best Practices

### 1. Always Test Incrementally

- Make one small change at a time
- Test immediately after each change
- Don't batch multiple changes together

### 2. Use Direct Values When Theme Callbacks Fail

- Theme callbacks may not work in all contexts
- Direct OKLCH values are more reliable
- Still provides theme system benefits

### 3. Preserve Functionality While Fixing Styles

- Keep all existing functionality working
- Don't remove important attributes like `data-debug-id`
- Maintain proper component structure

### 4. Verify with WebFetch Tool

- Always use webfetch to see actual HTML output
- Don't rely on assumptions about what's being generated
- Check both structure and styling

### 5. Background Server Logs Are Primary Debug Source

- Dev server logs in `.log/dev-server.log` contain exact error details
- Stack traces point to specific files and lines
- Background logging captures all server output including 500 errors
- Server logs show real-time compilation and runtime errors
- Use `grep` and `tail` commands to efficiently search logs
- Monitor logs in real-time with `tail -f .log/dev-server.log`
- Use server logs to guide codebase investigation

### 6. Document Issues and Solutions

- Note what didn't work and why
- Record the working solution
- Update documentation for future reference

## 🚨 Common Pitfalls

### 1. Searching Codebase Before Checking Server Logs

**Problem:** When webfetch returns 500 error, immediately searching codebase instead of checking server logs first.

**Solution:** ALWAYS check the `.log/dev-server.log` file first. Use `grep -i "500\|error" .log/dev-server.log` to find exact error messages, stack traces, and file locations. Only search codebase after understanding what the server logs reveal.

### 2. Not Testing After Each Change

**Problem:** Making multiple changes and then testing, making it hard to identify which change caused issues.

**Solution:** Test after every single change, no matter how small.

### 3. Starting Multiple Servers / Port Conflicts

**Problem:** Starting a new server without checking if one is already running, causing EADDRINUSE errors.

**Solution:** Always check for existing servers first and kill them before starting a new one. Use the background server management commands to properly start/stop servers with logging.

### 4. Forgetting to Start/Restart Server

**Problem:** Testing against a stale or crashed server.

**Solution:** Always verify the server is running with `ps -p $(cat .log/dev-server.pid)` and check logs for crashes. Restart if needed using the background server commands.

### 5. Not Checking HTML Output

**Problem:** Assuming styles are applied correctly without verifying the actual output.

**Solution:** Always use webfetch to inspect the generated HTML.

### 6. Breaking Existing Functionality

**Problem:** Focusing only on styling and accidentally removing important functionality.

**Solution:** Preserve all existing attributes, event handlers, and component structure.

### 7. Not Cleaning Up Old Logs

**Problem:** Old logs accumulate and make it difficult to identify current issues.

**Solution:** Always remove old logs with `rm -rf .log` before starting a new debugging session.

### 8. Not Monitoring Logs During Development

**Problem:** Missing real-time errors and issues as they occur.

**Solution:** Use `tail -f .log/dev-server.log` to monitor logs in real-time during development and testing.

---

## 🧹 Cleanup Commands

```bash
# Stop background server and clean up
kill $(cat .log/dev-server.pid 2>/dev/null) 2>/dev/null || true
rm -f .log/dev-server.pid

# Remove all logs
rm -rf .log

# Complete cleanup (server + logs)
pkill -f "bun.*$(basename $(pwd))" || true
rm -rf .log
```

<system-reminder>
Always clean up background servers and logs after debug/investigation
Use the cleanup commands to properly stop background processes
</system-reminder>

This debugging workflow ensures systematic identification and resolution of web application issues while maintaining code quality and functionality through comprehensive background logging.
