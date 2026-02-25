# Manual Testing Checklist for Soccer Timekeeper App

This document provides a comprehensive checklist for manual testing of the Soccer Timekeeper App. These tests complement the automated test suite and verify aspects that require human judgment or specific hardware (mobile devices, cameras).

## Prerequisites

- [ ] Application is running locally (`streamlit run app.py`)
- [ ] Mobile device with camera available for QR code scanning
- [ ] Multiple browser windows/tabs available for multi-user testing
- [ ] Stable internet connection (if deployed remotely)

## 1. Visual Theme Consistency

### Green Soccer Theme
- [ ] Home screen displays green color scheme (background: light green #e8f5e9)
- [ ] All buttons are green (#2e7d32) with white text
- [ ] Headers and titles are dark green (#1b5e20)
- [ ] Timer display has green text on light green background
- [ ] Theme is consistent across all screens (Home, Create Timer, Get Timer, Active Timers, Timer Detail)
- [ ] Button hover effects work correctly (darker green on hover)
- [ ] No visual glitches or color inconsistencies

### Layout and Spacing
- [ ] Title "⚽ TIME KEEPER ⚽" is centered and prominent on home screen
- [ ] Buttons are properly sized and aligned
- [ ] Adequate spacing between UI elements
- [ ] Timer display is large and easy to read (72px font)
- [ ] QR code is displayed at appropriate size for scanning

## 2. Navigation Flows

### Home Screen Navigation
- [ ] "Create Timer" button navigates to Create Timer screen
- [ ] "Get Timer" button navigates to Get Timer screen
- [ ] "Active Timers" button navigates to Active Timers screen

### Back Navigation
- [ ] "← Back to Home" button works from Create Timer screen
- [ ] "← Back to Home" button works from Get Timer screen
- [ ] "← Back to Home" button works from Active Timers screen
- [ ] "← Back to Active Timers" button works from Timer Detail screen

### Deep Navigation
- [ ] Clicking "View" on a match in Active Timers navigates to Timer Detail screen
- [ ] Selected match is correctly displayed in Timer Detail screen
- [ ] Navigation preserves user context (user ID, match list)

## 3. Admin Workflow: Create → Control → Stop

### Match Creation
- [ ] Enter match description (e.g., "Championship Final")
- [ ] Click "Create Timer" button
- [ ] Match is created successfully
- [ ] QR code is displayed
- [ ] Match ID is displayed
- [ ] Timer shows "01:30:00" initially
- [ ] Admin controls are visible (Start, Reset, Stop buttons)

### Timer Control - Start
- [ ] Click "▶ Start" button
- [ ] Button changes to "⏸ Pause"
- [ ] Timer starts counting down
- [ ] Timer updates every second
- [ ] Status shows "Running"
- [ ] Role shows "Admin"

### Timer Control - Pause
- [ ] Click "⏸ Pause" button while timer is running
- [ ] Button changes to "▶ Start"
- [ ] Timer stops counting down
- [ ] Timer value is preserved
- [ ] Status shows "Paused"

### Timer Control - Resume
- [ ] Click "▶ Start" button while timer is paused
- [ ] Button changes to "⏸ Pause"
- [ ] Timer resumes counting down from paused value
- [ ] Status shows "Running"

### Timer Control - Reset
- [ ] Let timer run for a few seconds
- [ ] Click "↻ Reset" button
- [ ] Timer resets to "01:30:00"
- [ ] Timer is paused (not running)
- [ ] Status shows "Paused"

### Timer Control - Stop
- [ ] Click "⏹ Stop" button
- [ ] Success message is displayed
- [ ] Screen returns to home screen
- [ ] Match is marked as inactive

## 4. Spectator Workflow: Scan → View → Follow

### QR Code Scanning (Mobile Device)
- [ ] Open app on mobile device
- [ ] Navigate to "Get Timer" screen
- [ ] QR scanner interface is displayed
- [ ] Point camera at QR code from admin's screen
- [ ] QR code is scanned successfully
- [ ] Match is added to user's list
- [ ] Success message is displayed
- [ ] Screen navigates to Active Timers

### Manual UUID Entry (Fallback)
- [ ] Navigate to "Get Timer" screen
- [ ] Scroll to "Or Enter Match ID Manually" section
- [ ] Copy Match ID from admin's screen
- [ ] Paste Match ID into text input
- [ ] Click "Add Match" button
- [ ] Match is added to user's list
- [ ] Success message is displayed
- [ ] Screen navigates to Active Timers

### View Match Details
- [ ] Match appears in Active Timers list
- [ ] Match description is displayed correctly
- [ ] Match ID is displayed correctly
- [ ] Time remaining is displayed correctly
- [ ] Status (Running/Paused) is displayed correctly
- [ ] Click "👁 View" button
- [ ] Timer Detail screen is displayed
- [ ] Large timer display is visible
- [ ] Role shows "Spectator"

### Spectator View Restrictions
- [ ] Admin controls (Pause, Resume, Reset, Stop) are NOT visible
- [ ] Only timer and match information are displayed
- [ ] Timer updates in real-time
- [ ] Status updates when admin changes timer state

### Follow Match Updates
- [ ] Admin pauses timer on their screen
- [ ] Spectator's screen updates to show "Paused" status
- [ ] Admin resumes timer
- [ ] Spectator's screen updates to show "Running" status
- [ ] Timer values are synchronized (within 2 seconds)

### Remove Match from List
- [ ] Navigate to Active Timers screen
- [ ] Click "🗑 Delete" button for a match
- [ ] Success message is displayed
- [ ] Match is removed from list
- [ ] Match is no longer visible in Active Timers

## 5. Timer Synchronization Across Multiple Users

### Setup
- [ ] Open app in Browser Window 1 (Admin)
- [ ] Open app in Browser Window 2 (Spectator 1)
- [ ] Open app in Browser Window 3 (Spectator 2)
- [ ] Admin creates a match
- [ ] Spectators add match to their lists (via QR or manual entry)

### Synchronization Testing
- [ ] All users view the same match in Timer Detail screen
- [ ] Admin starts timer
- [ ] All users see timer counting down
- [ ] Timer values are synchronized across all windows (within 2 seconds)
- [ ] Admin pauses timer
- [ ] All users see "Paused" status
- [ ] Timer values remain consistent while paused
- [ ] Admin resumes timer
- [ ] All users see "Running" status
- [ ] Timer continues counting down for all users
- [ ] Admin resets timer
- [ ] All users see timer reset to "01:30:00"

## 6. QR Code Scanning on Mobile Devices

### iOS Testing
- [ ] Open app on iPhone/iPad
- [ ] Navigate to "Get Timer" screen
- [ ] Camera permission is requested (if first time)
- [ ] Grant camera permission
- [ ] QR scanner displays camera feed
- [ ] Scan QR code from another device
- [ ] QR code is decoded successfully
- [ ] Match is added to list

### Android Testing
- [ ] Open app on Android device
- [ ] Navigate to "Get Timer" screen
- [ ] Camera permission is requested (if first time)
- [ ] Grant camera permission
- [ ] QR scanner displays camera feed
- [ ] Scan QR code from another device
- [ ] QR code is decoded successfully
- [ ] Match is added to list

### QR Code Quality
- [ ] QR code is clear and scannable
- [ ] QR code has sufficient contrast (black on white)
- [ ] QR code size is appropriate for mobile scanning
- [ ] QR code scans successfully from various distances (10-30cm)
- [ ] QR code scans successfully in different lighting conditions

## 7. Data Persistence Across Page Refreshes

### Match State Persistence
- [ ] Create a match and start timer
- [ ] Let timer run for 10-15 seconds
- [ ] Note the current time value
- [ ] Refresh the page (F5 or Ctrl+R)
- [ ] Navigate back to the match
- [ ] Timer continues from approximately the same value (within 2 seconds)
- [ ] Timer state (running/paused) is preserved
- [ ] Match description and ID are preserved

### User Match List Persistence
- [ ] Add 2-3 matches to your list
- [ ] Note the matches in your list
- [ ] Refresh the page (F5 or Ctrl+R)
- [ ] Navigate to Active Timers
- [ ] All matches are still in your list
- [ ] Match details are preserved

### Session Persistence
- [ ] Create a match as admin
- [ ] Refresh the page
- [ ] Navigate back to the match
- [ ] Admin controls are still visible (you're still the admin)
- [ ] User ID is preserved across refresh

## 8. Error Handling and Edge Cases

### Invalid UUID Entry
- [ ] Navigate to "Get Timer" screen
- [ ] Enter invalid UUID format (e.g., "not-a-uuid")
- [ ] Click "Add Match"
- [ ] Error message is displayed: "Invalid UUID format"
- [ ] No crash or unexpected behavior

### Non-Existent Match UUID
- [ ] Navigate to "Get Timer" screen
- [ ] Enter valid UUID format but non-existent match (e.g., "550e8400-e29b-41d4-a716-446655440000")
- [ ] Click "Add Match"
- [ ] Error message is displayed: "Match UUID does not exist in storage"
- [ ] No crash or unexpected behavior

### Empty Match Description
- [ ] Navigate to "Create Timer" screen
- [ ] Leave match description empty
- [ ] Click "Create Timer"
- [ ] Error message is displayed: "Match description cannot be empty"
- [ ] No match is created

### QR Scanner Unavailable
- [ ] Navigate to "Get Timer" screen on device without camera
- [ ] Warning message is displayed about QR scanner unavailability
- [ ] Manual entry option is still available
- [ ] Can successfully add match via manual entry

### Timer at Zero
- [ ] Create a match and start timer
- [ ] Wait for timer to reach 00:00:00 (or manually set for testing)
- [ ] Timer stops at 00:00:00
- [ ] Timer does not go negative
- [ ] Status shows "Paused"

### Stopped Match Behavior
- [ ] Create a match and stop it
- [ ] Match disappears from Active Timers list
- [ ] Match cannot be controlled anymore
- [ ] Spectators see match as inactive

## 9. Responsive Design and Mobile Experience

### Mobile Layout
- [ ] Open app on mobile device (phone)
- [ ] All screens are readable and usable
- [ ] Buttons are large enough to tap easily
- [ ] Text is readable without zooming
- [ ] Timer display is prominent and clear
- [ ] No horizontal scrolling required

### Tablet Layout
- [ ] Open app on tablet device
- [ ] Layout adapts appropriately
- [ ] All features are accessible
- [ ] UI elements are properly sized

### Desktop Layout
- [ ] Open app on desktop browser
- [ ] Layout is centered and well-proportioned
- [ ] All features are accessible
- [ ] UI is not stretched or cramped

## 10. Performance and Usability

### Timer Update Performance
- [ ] Timer updates smoothly every second
- [ ] No visible lag or stuttering
- [ ] Page remains responsive during timer updates
- [ ] No excessive CPU usage

### Navigation Performance
- [ ] Screen transitions are smooth
- [ ] No noticeable delay when navigating
- [ ] Back buttons respond immediately
- [ ] No loading spinners or delays

### Multi-Match Performance
- [ ] Add 5-10 matches to your list
- [ ] Active Timers screen displays all matches
- [ ] All timers update smoothly
- [ ] No performance degradation
- [ ] Page remains responsive

### User Experience
- [ ] All buttons have clear labels and icons
- [ ] Error messages are helpful and actionable
- [ ] Success messages provide clear feedback
- [ ] Navigation is intuitive
- [ ] No confusing or ambiguous UI elements

## Test Results Summary

**Date:** _______________  
**Tester:** _______________  
**Environment:** _______________  

**Overall Results:**
- [ ] All tests passed
- [ ] Some tests failed (document below)
- [ ] Critical issues found (document below)

**Issues Found:**

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Notes:**

_______________________________________________
_______________________________________________
_______________________________________________

## Sign-off

**Tester Signature:** _______________  
**Date:** _______________  
**Status:** [ ] Approved [ ] Needs Fixes
