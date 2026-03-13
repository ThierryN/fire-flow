# Quiz Integration & Testing Guide

## Overview

This guide covers how to integrate the quiz/assessment system with your MERN LMS and test the complete end-to-end flow.

## Architecture

### Components
- **QuizPlayer.jsx** - Main quiz orchestrator (uses useQuizAPI hook)
- **QuestionDisplay.jsx** - Renders 6 question types
- **AnswerRecorder.jsx** - Captures and auto-saves answers
- **ResultsView.jsx** - Displays results and leaderboard
- **QuizHeader.jsx** - Progress bar and timer
- **QuizPage.jsx** - Page wrapper with routing

### Hooks
- **useQuizAPI.js** - Custom hook for all 18 API endpoints
  - Handles authentication
  - Manages loading states
  - Implements retry logic with exponential backoff
  - Centralizes error handling

### Error Handling
- **ErrorBoundary.jsx** - Catches React errors
  - Displays user-friendly error messages
  - Development error details
  - Recovery actions

## Setup Instructions

### 1. Install Dependencies (if needed)

```bash
cd client
npm install axios  # If not already installed
```

### 2. Update Router Configuration

Add quiz route to your main App.jsx or routing file:

```jsx
import QuizPage from './pages/QuizPage';

// In your routes configuration:
{
  path: '/courses/:courseId/assessments/:assessmentId',
  element: <QuizPage />,
}
```

### 3. Verify API Server is Running

```bash
cd server
npm start
```

Check health endpoint:
```bash
curl http://localhost:5000/api/health
# Should return: {"status":"success","message":"API is running"}
```

### 4. Create Test Data (Optional)

Seeds database with 6 sample questions (one of each type):

```bash
node server/seed-assessment-data.js
```

Output will show:
- Assessment ID
- Questions created
- Next steps

## Testing Workflow

### Phase 1: Endpoint Verification

Test all 18 endpoints:

```bash
node test-quiz-e2e.js
```

Expected output:
```
✓ API is running
✓ Fetch questions
✓ Create attempt
✓ Save answer (Auto-save)
✓ Get stats
✓ Submit quiz
✓ Get answers
✓ Get student attempts

Pass Rate: 100%
```

### Phase 2: Component Testing

#### Manual Testing in Browser

1. **Start dev server:**
   ```bash
   cd client
   npm start
   ```

2. **Navigate to quiz:**
   ```
   http://localhost:3000/courses/course-001/assessments/assessment-001
   ```

3. **Test quiz flow:**
   - ✅ Quiz loads with "Ready to Start" intro
   - ✅ Click "Start Quiz" - quiz begins
   - ✅ Questions display correctly
   - ✅ Navigate between questions using Next/Previous
   - ✅ Click question numbers to jump
   - ✅ Answers auto-save (watch for save indicator)
   - ✅ Progress bar updates
   - ✅ Timer increments
   - ✅ Submit quiz
   - ✅ Results display with score

#### Test All Question Types

1. **Multiple Choice**
   - Select radio button option
   - Answer auto-saves
   - Selected value persists

2. **True/False**
   - Select yes/no option
   - Reflects in answer tracker

3. **Short Answer**
   - Type text (< 500 chars)
   - Auto-saves after 1 second

4. **Essay**
   - Type long text (< 5000 chars)
   - Auto-saves with debounce

5. **Matching**
   - Drag premises to responses
   - Saves matched pairs

6. **Fill in the Blank**
   - Fill multiple input fields
   - All blanks auto-saved

### Phase 3: Error Handling Testing

#### Test Error Scenarios

1. **API Error - Server Offline**
   - Stop server: `ctrl+c` in server terminal
   - Refresh quiz page
   - Should show: "Failed to load questions"
   - Button to "Try Again"

2. **API Error - Invalid Token**
   - Modify stored JWT token in localStorage
   - Load quiz
   - Should show: "Authentication failed"

3. **Network Timeout**
   - Throttle network (DevTools Network tab)
   - Slow 3G or Offline
   - Should retry automatically

4. **React Component Error**
   - Check browser console for errors
   - ErrorBoundary should catch
   - Show recovery options

### Phase 4: Performance Testing

#### Response Times

```bash
# Time question loading
curl -w "@curl-format.txt" http://localhost:5000/api/assessments/test-001/questions

# Expected:
# Time to first byte: < 50ms
# Total time: < 100ms
```

#### Auto-save Performance

- Type answer in text field
- Watch network tab
- Auto-save should debounce (1 second)
- No rapid consecutive requests

#### Large Quizzes

- Test with 50+ questions
- Sidebar should scroll
- Navigation should be responsive
- Memory usage should be stable

## API Integration Details

### Authentication

All endpoints require JWT token in header:

```javascript
// Automatically handled by useQuizAPI hook
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
}
```

### Request/Response Format

**Request:**
```javascript
{
  question_id: "uuid",
  answer: { ... },
  timestamp: "2025-10-19T03:37:00Z"
}
```

**Response:**
```javascript
{
  success: true,
  data: {
    id: "uuid",
    status: "saved",
    saved_at: "2025-10-19T03:37:00Z"
  }
}
```

### Error Handling

```javascript
// Auto-retry with exponential backoff
// Attempt 1: immediate
// Attempt 2: 1 second wait
// Attempt 3: 2 second wait
// Attempt 4: 4 second wait
// Gives up after 3 retries
```

## Troubleshooting

### Issue: "Failed to load questions"

**Cause:** Assessment has no questions
**Solution:** 
```bash
node server/seed-assessment-data.js
```

### Issue: "Authentication failed"

**Cause:** Invalid or expired token
**Solution:** 
- Login again
- Check localStorage for 'token' key
- Verify token is still valid

### Issue: Auto-save not working

**Cause:** attemptId not set
**Check:** 
```javascript
// In browser console
localStorage.getItem('token')  // Should exist
// Network tab should show POST requests every 1 second
```

### Issue: Results not displaying

**Cause:** leaderboard endpoint not implemented
**Workaround:** Results still show without leaderboard

### Issue: Components not rendering

**Cause:** React Router not configured
**Solution:** Verify QuizPage route in App.jsx

## Environment Variables

Create `.env` file in client directory:

```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENABLE_DEBUG=true
```

## Monitoring & Debugging

### Browser DevTools

**Network Tab:**
- Monitor API requests
- Check response times
- Verify auth headers

**Console Tab:**
- Look for error messages
- Check useQuizAPI logs
- Watch for warnings

**React DevTools Extension:**
- Inspect component props
- Check state updates
- Monitor re-renders

### Server Logs

```bash
# Watch server logs
node server/server.js

# Look for:
# - Authentication errors
# - Database connection issues
# - Missing endpoints
```

## Production Checklist

- [ ] All 18 endpoints tested
- [ ] Error boundaries in place
- [ ] Auth tokens properly managed
- [ ] API errors gracefully handled
- [ ] Loading states display correctly
- [ ] Auto-save works reliably
- [ ] Results display properly
- [ ] Mobile responsive tested
- [ ] Browser compatibility verified
- [ ] Performance acceptable
- [ ] Error logging configured
- [ ] Environment variables set

## Performance Optimization

### Already Implemented
- Debounced auto-save (1 second)
- Memoized callbacks (useCallback)
- Lazy loading of questions
- CSS transitions (hardware accelerated)
- Retry logic with exponential backoff

### Future Improvements
- Code splitting components
- Service Workers for offline support
- Compression on large responses
- Caching strategy
- Request batching

## Support & Documentation

- **API Documentation:** See assessment/README.md
- **Component Props:** Check JSDoc comments in components
- **Error Codes:** See server error responses
- **Integration Examples:** See QuizPage.jsx

## Next Steps

1. ✅ Verify API endpoints operational
2. ✅ Test quiz flow in browser
3. ✅ Test error handling
4. ✅ Monitor performance
5. 🔄 Deploy to staging
6. 🔄 User acceptance testing
7. 🔄 Deploy to production

---

**Last Updated:** October 19, 2025  
**Status:** Ready for Integration Testing
