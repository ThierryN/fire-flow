# Zoom Integration - Complete Testing Checklist
**Purpose**: Verify all Zoom features work end-to-end
**Time Required**: ~30 minutes
**Status**: Ready to execute after scope cleanup

---

## ✅ Pre-Testing Checklist

Before starting tests:

- [ ] Scopes cleaned up (keep only 4 essential)
- [ ] Server running: `npm run dev`
- [ ] Browser opened: `http://localhost:3000`
- [ ] Logged in as teacher
- [ ] Another browser window open as student (or separate device)

---

## 🧪 Phase 1: Authentication & Connection (5 min)

### Test 1.1: Verify Credentials
```bash
cd server
node test-zoom-connection.js
```

**Expected Result**:
```
✅ ✅ ✅ All Tests Passed!
✅ Access token obtained
✅ User info retrieved
✅ Meetings found: 10
```

- [ ] Test passes
- [ ] Access token shown
- [ ] Account name: "School of the Holy Spirit"
- [ ] 10 meetings listed

### Test 1.2: Debug Auth (Optional)
```bash
node debug-zoom-auth.js
```

**Expected Result**:
```
✅ SUCCESS!
Access Token: [valid token]
Token Type: bearer
Expires In: 3599 seconds
```

- [ ] Shows SUCCESS
- [ ] Token generated
- [ ] Expiry correct

---

## 🎬 Phase 2: Create Meeting (5 min)

### Test 2.1: Teacher Creates Meeting

**Steps**:
1. Login as teacher
2. Go to course page
3. Click "Create Meeting" button
4. Fill in:
   - Title: "Test Meeting - [Date]"
   - Date/Time: Tomorrow at 2 PM
   - Duration: 60 minutes
5. Click "Create"

**Expected Result**:
- [ ] Meeting created successfully
- [ ] Success message shown
- [ ] Meeting appears in dashboard
- [ ] Meeting link provided
- [ ] Can copy join URL

### Test 2.2: Verify in Zoom Account

**Steps**:
1. Go to: https://zoom.us/signin
2. Login with Zoom account
3. Go to "My Meetings"

**Expected Result**:
- [ ] New test meeting appears in list
- [ ] Meeting title matches what was entered
- [ ] Meeting time is correct
- [ ] Meeting ID is shown

---

## 👥 Phase 3: Student Joins Meeting (5 min)

### Test 3.1: Student Accesses Meeting

**Steps**:
1. Logout as teacher
2. Login as student
3. Go to course enrollment page
4. Enroll in the teacher's course
5. Go to "Active Meetings" section
6. See the newly created meeting
7. Click "Join Meeting"

**Expected Result**:
- [ ] Student can see meeting in their dashboard
- [ ] "Join Meeting" button visible
- [ ] Click button loads Zoom meeting
- [ ] Zoom SDK initializes
- [ ] Can see meeting join screen

### Test 3.2: Join Meeting

**Steps**:
1. Click "Join" in Zoom meeting dialog
2. Wait for Zoom to load
3. Check audio/video settings
4. Enter meeting

**Expected Result**:
- [ ] Meeting loads successfully
- [ ] Can see meeting participant list
- [ ] Microphone/camera working (or can toggle)
- [ ] Can see meeting controls
- [ ] Meeting recorded (if auto-recording enabled)

---

## 📊 Phase 4: Attendance Tracking (5 min)

### Test 4.1: Verify Attendance Recorded

**Steps**:
1. Both teacher and student in meeting
2. Wait 30 seconds
3. Teacher: Go back to course page
4. Click "Meeting Details"
5. Look for attendance section

**Expected Result**:
- [ ] Student appears in attendance list
- [ ] Join time recorded
- [ ] Duration shows correct time
- [ ] Status shows "Attended"

### Test 4.2: Manual Attendance (Optional)

**Steps**:
1. Teacher marks manual attendance
2. System records additional entry

**Expected Result**:
- [ ] Manual entry recorded
- [ ] Can edit attendance if needed

---

## 🎤 Phase 5: Q&A System (5 min)

### Test 5.1: Student Asks Question

**Steps** (while in meeting):
1. Student opens Q&A panel
2. Types question: "Can you explain this concept?"
3. Posts question
4. Check if visible to teacher

**Expected Result**:
- [ ] Question appears in Q&A section
- [ ] Shows student name
- [ ] Shows timestamp
- [ ] Teacher can see it

### Test 5.2: Teacher Answers

**Steps**:
1. Teacher sees question in Q&A
2. Clicks "Answer"
3. Types response
4. Submits

**Expected Result**:
- [ ] Answer appears under question
- [ ] Student can see answer
- [ ] Shows "Answered" status
- [ ] Both can see conversation thread

---

## 📹 Phase 6: Recording Access (10 min)

### Test 6.1: Wait for Recording

**Steps**:
1. After meeting ends, wait 1-2 hours (Zoom processes)
2. Check course page
3. Look for "Recordings" section

**Expected Result**:
- [ ] Recording appears after processing
- [ ] Shows duration
- [ ] Shows creation date
- [ ] Shows file size

### Test 6.2: Student Watches Recording

**Steps**:
1. Student views available recordings
2. Clicks recording
3. Player loads
4. Plays recording

**Expected Result**:
- [ ] Recording accessible to enrolled students
- [ ] Player loads
- [ ] Can play/pause
- [ ] Can seek to different times
- [ ] Shows transcript (if available)

### Test 6.3: Teacher Manages Recording

**Steps**:
1. Teacher can see recording
2. Can view recording details
3. Can share or restrict access

**Expected Result**:
- [ ] Teacher has full recording access
- [ ] Can control visibility
- [ ] Can download recording
- [ ] Can delete if needed

---

## 🎯 Phase 7: Video Features Integration (5 min)

### Test 7.1: Video Bookmarks

**Steps**:
1. Upload a test video to lesson
2. Open video player
3. Click at various points to create bookmarks
4. Refresh page
5. Check bookmarks persist

**Expected Result**:
- [ ] Can create bookmarks
- [ ] Bookmarks show as colored bars
- [ ] Click bar to jump to timestamp
- [ ] Bookmarks saved after refresh
- [ ] Can delete bookmarks

### Test 7.2: YouTube Video Progression

**Steps**:
1. Add YouTube video to lesson
2. Start watching (play for 30 seconds)
3. Pause and close page
4. Reopen course
5. Video should show progress and offer resume

**Expected Result**:
- [ ] Progress saved automatically
- [ ] "Resume at X:XX?" button appears
- [ ] Click Resume jumps to saved position
- [ ] Works after page refresh
- [ ] Works across multiple sessions

---

## 💳 Phase 8: E-Commerce Integration (5 min)

### Test 8.1: Shop Products

**Steps**:
1. Go to Shop page
2. See products available for sale
3. Click on product
4. See product details
5. Click "Add to Cart"

**Expected Result**:
- [ ] Products display correctly
- [ ] Images load
- [ ] Prices shown
- [ ] Product added to cart
- [ ] Cart counter updates

### Test 8.2: Checkout

**Steps**:
1. Go to cart
2. Review items
3. Click "Checkout"
4. Enter shipping/billing info
5. Click "Pay with PayPal"

**Expected Result**:
- [ ] Cart shows correct items
- [ ] Form accepts information
- [ ] PayPal window opens
- [ ] Can complete payment

### Test 8.3: Payment Success (Optional - Test Mode)

**Steps**:
1. Complete PayPal payment
2. Return to site
3. Check order confirmation page

**Expected Result**:
- [ ] Payment processed
- [ ] Order confirmation shown
- [ ] Order appears in "My Orders"
- [ ] Invoice available

---

## 📊 Phase 9: Integration Test (5 min)

### Test 9.1: Complete Student Journey

**Steps**:
1. New student enrolls in course
2. Watches videos (with bookmarks)
3. Attends virtual meeting
4. Watches meeting recording
5. Buys related product
6. Completes order

**Expected Result**:
- [ ] Complete journey works
- [ ] All features functional
- [ ] No errors or breaks
- [ ] Data persists across sessions

---

## 🚨 Phase 10: Error Handling (5 min)

### Test 10.1: Meeting Not Started

**Steps**:
1. Try to join meeting that hasn't started yet
2. Should show appropriate message

**Expected Result**:
- [ ] Error message clear
- [ ] Can try again later
- [ ] Doesn't break app

### Test 10.2: Recording Not Available

**Steps**:
1. Check recording before it's processed
2. Should show "Processing" status

**Expected Result**:
- [ ] Clear status message
- [ ] Can refresh to check
- [ ] Doesn't show error

### Test 10.3: Network Issues

**Steps**:
1. Disconnect internet
2. Try to load meeting
3. Reconnect internet

**Expected Result**:
- [ ] Clear error message
- [ ] Can retry
- [ ] Doesn't crash app

---

## ✅ Final Verification

### System Checks
- [ ] No console errors
- [ ] All page loads are fast
- [ ] Buttons are responsive
- [ ] Forms validate correctly
- [ ] Data persists after refresh
- [ ] Works in different browsers (Chrome, Firefox, Safari)

### Performance Checks
- [ ] Page loads in < 3 seconds
- [ ] Zoom features load smoothly
- [ ] Video players responsive
- [ ] No lag or stuttering
- [ ] Smooth scrolling

### Security Checks
- [ ] Credentials not exposed
- [ ] HTTPS in production
- [ ] User data protected
- [ ] Proper access control
- [ ] No sensitive info in logs

---

## 🎓 Test Data Needed

Before starting tests, prepare:

**As Teacher**:
- [ ] 1 test course
- [ ] 1 test video (uploaded)
- [ ] 1 YouTube video link
- [ ] Test product ($9.99)

**As Student**:
- [ ] Different login account
- [ ] Enrolled in test course
- [ ] Valid email

**As Admin** (if testing):
- [ ] Admin access
- [ ] Can view all meetings
- [ ] Can view analytics

---

## 📋 Test Execution Log

### Test #1: Authentication
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #2: Create Meeting
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #3: Join Meeting
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #4: Attendance
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #5: Q&A
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #6: Recordings
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #7: Videos
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

### Test #8: E-Commerce
- **Date**: ___________
- **Status**: ☐ Pass ☐ Fail
- **Notes**: _____________________

---

## 🏁 Overall Test Results

```
Total Tests: 10 phases
Passed: ___/10
Failed: ___/10
Success Rate: ____%

Issues Found:
☐ None
☐ Minor (cosmetic)
☐ Major (functionality)
☐ Critical (system down)
```

**Overall Status**: ☐ PASS ☐ FAIL

---

## 📝 Issues Found

| Issue | Severity | Resolution | Status |
|-------|----------|-----------|--------|
| | HIGH | | ☐ Open ☐ Fixed |
| | MEDIUM | | ☐ Open ☐ Fixed |
| | LOW | | ☐ Open ☐ Fixed |

---

## ✨ Ready to Test?

All systems are configured. Follow this checklist phase by phase.

**Estimated Time**: 30 minutes for full testing

**Success Criteria**: All tests pass

**Confidence**: 🟢 HIGH - All systems ready

---

**Start Testing When Ready!** ✅
