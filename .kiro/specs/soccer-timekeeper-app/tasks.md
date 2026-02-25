# Implementation Plan: Soccer Timekeeper App

## Overview

This implementation plan breaks down the Soccer Timekeeper App into discrete coding tasks. The app is a Streamlit-based web application that enables match administrators to create 90-minute soccer match timers and share them via QR codes, while spectators can scan codes to follow matches in real-time. The implementation follows a layered architecture with data models, business logic managers, storage layer, and UI components.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (data/, tests/, src/)
  - Create requirements.txt with Streamlit, qrcode, streamlit-qrcode-scanner, hypothesis, pytest
  - Create config.py with application constants (timer duration, colors, storage paths)
  - Initialize storage directory and .gitignore
  - _Requirements: 8.1_

- [x] 2. Implement core data models
  - [x] 2.1 Create data model classes
    - Define TimerState dataclass with seconds_remaining, is_running, last_update, total_paused_time
    - Define Match dataclass with match_uuid, description, admin_id, timer_state, created_at, is_active
    - Define User dataclass with user_id and match_list
    - _Requirements: 1.3, 1.4, 8.1_

  - [x] 2.2 Write property test for match persistence round-trip
    - **Property 4: Match Persistence Round-Trip**
    - **Validates: Requirements 1.4, 8.1**

- [ ] 3. Implement storage layer
  - [x] 3.1 Create StorageManager class with JSON file operations
    - Implement save_match() with file locking for concurrent access
    - Implement load_match() with error handling for missing/corrupted files
    - Implement save_user_data() and load_user_data() methods
    - Implement list_all_matches() for retrieving all stored matches
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 3.2 Write property test for match persistence
    - **Property 4: Match Persistence Round-Trip**
    - **Validates: Requirements 1.4, 8.1**

  - [x] 3.3 Write property test for user match list persistence
    - **Property 23: User Match List Persistence**
    - **Validates: Requirements 8.3**

  - [x] 3.4 Write unit tests for storage error handling
    - Test file not found scenarios
    - Test JSON parsing errors
    - Test concurrent access handling
    - _Requirements: 8.1_

- [x] 4. Implement TimerManager
  - [x] 4.1 Create TimerManager class with timer operations
    - Implement initialize_timer() returning TimerState at 5400 seconds
    - Implement tick() to decrement timer by 1 second if running and > 0
    - Implement pause() to set is_running to false
    - Implement resume() to set is_running to true
    - Implement reset() to set seconds to 5400 and is_running to false
    - Implement format_time() to convert seconds to HH:MM:SS string
    - Implement get_elapsed_time() to calculate time accounting for pauses
    - _Requirements: 1.3, 4.1, 4.2, 4.5, 5.2, 5.3, 5.4_

  - [x] 4.2 Write property test for timer initialization
    - **Property 3: Timer Initialization**
    - **Validates: Requirements 1.3**

  - [x] 4.3 Write property test for time formatting
    - **Property 5: Time Formatting**
    - **Validates: Requirements 1.6, 3.3, 4.3**

  - [ ]* 4.4 Write property test for timer countdown
    - **Property 13: Timer Countdown**
    - **Validates: Requirements 4.1**

  - [ ]* 4.5 Write property test for timer zero boundary
    - **Property 14: Timer Zero Boundary**
    - **Validates: Requirements 4.2**

  - [ ]* 4.6 Write property test for paused timer idempotence
    - **Property 15: Paused Timer Idempotence**
    - **Validates: Requirements 4.5**

  - [ ]* 4.7 Write property test for pause action
    - **Property 16: Pause Action**
    - **Validates: Requirements 5.2**

  - [ ]* 4.8 Write property test for resume action
    - **Property 17: Resume Action**
    - **Validates: Requirements 5.3**

  - [ ]* 4.9 Write property test for reset action
    - **Property 18: Reset Action**
    - **Validates: Requirements 5.4**

  - [ ]* 4.10 Write unit tests for timer edge cases
    - Test timer at exactly 0 seconds
    - Test timer state transitions
    - Test format_time with boundary values (0, 5400)
    - _Requirements: 4.1, 4.2_

- [x] 5. Implement MatchManager
  - [x] 5.1 Create MatchManager class with match operations
    - Implement create_match() to generate UUID, initialize timer, create Match object
    - Implement get_match() to retrieve match by UUID from storage
    - Implement update_match() to persist match state changes
    - Implement delete_match() to set is_active to false
    - Implement list_active_matches() to filter and return active matches
    - Implement update_timer_display() to calculate elapsed time and update timer
    - _Requirements: 1.1, 1.3, 1.4, 3.5, 5.5, 8.2, 8.5_

  - [ ]* 5.2 Write property test for UUID uniqueness
    - **Property 1: UUID Uniqueness**
    - **Validates: Requirements 1.1**

  - [ ]* 5.3 Write property test for stop action
    - **Property 19: Stop Action**
    - **Validates: Requirements 5.5**

  - [ ]* 5.4 Write property test for timer accuracy after reload
    - **Property 24: Timer Accuracy After Reload**
    - **Validates: Requirements 8.5**

  - [ ]* 5.5 Write unit tests for match operations
    - Test create_match with valid description
    - Test get_match with non-existent UUID
    - Test delete_match sets is_active to false
    - _Requirements: 1.1, 1.4, 5.5_

- [x] 6. Implement QRCodeManager
  - [x] 6.1 Create QRCodeManager class with QR operations
    - Implement generate_qr_code() using qrcode library to create PIL Image
    - Implement validate_uuid() to check UUID v4 format
    - Implement extract_uuid_from_scan() to parse and validate scanned data
    - Add error handling for QR generation failures
    - _Requirements: 1.2, 2.2, 2.4, 2.6, 9.1, 9.2, 9.3, 9.4_

  - [ ]* 6.2 Write property test for QR code round-trip
    - **Property 2: QR Code Round-Trip**
    - **Validates: Requirements 1.2, 2.2, 9.1, 9.3, 9.4**

  - [ ]* 6.3 Write property test for UUID format validation
    - **Property 8: UUID Format Validation**
    - **Validates: Requirements 2.6**

  - [ ]* 6.4 Write property test for invalid QR code handling
    - **Property 7: Invalid QR Code Handling**
    - **Validates: Requirements 2.4**

  - [ ]* 6.5 Write unit tests for QR code operations
    - Test generate_qr_code returns valid PIL Image
    - Test validate_uuid with valid and invalid formats
    - Test extract_uuid_from_scan with malformed data
    - _Requirements: 1.2, 2.4, 2.6_

- [x] 7. Implement UserManager
  - [x] 7.1 Create UserManager class with user operations
    - Implement get_or_create_user_id() using Streamlit session state
    - Implement add_match_to_user() to append UUID to user's match list
    - Implement remove_match_from_user() to remove UUID from match list
    - Implement get_user_matches() to retrieve user's match list
    - Persist user data to storage after modifications
    - _Requirements: 2.3, 3.5, 8.3_

  - [ ]* 7.2 Write property test for match list addition
    - **Property 6: Match List Addition**
    - **Validates: Requirements 2.3**

  - [ ]* 7.3 Write property test for match list deletion
    - **Property 12: Match List Deletion**
    - **Validates: Requirements 3.5**

  - [ ]* 7.4 Write unit tests for user operations
    - Test get_or_create_user_id creates new ID if not in session
    - Test add_match_to_user appends to list
    - Test remove_match_from_user removes from list
    - _Requirements: 2.3, 3.5_

- [x] 8. Implement AccessControlManager
  - [x] 8.1 Create AccessControlManager class with permission checks
    - Implement is_admin() to compare user_id with match.admin_id
    - Implement can_control_timer() to check admin status
    - Implement can_view_match() to check if user has access
    - _Requirements: 5.1, 6.1, 6.2_

  - [ ]* 8.2 Write property test for admin control visibility
    - **Property 20: Admin Control Visibility**
    - **Validates: Requirements 5.1, 5.7, 5.8**

  - [ ]* 8.3 Write property test for spectator view restrictions
    - **Property 21: Spectator View Restrictions**
    - **Validates: Requirements 6.1, 6.2**

  - [ ]* 8.4 Write unit tests for access control
    - Test is_admin returns true for match creator
    - Test is_admin returns false for other users
    - Test can_control_timer for admin and spectator
    - _Requirements: 5.1, 6.1, 6.2_

- [x] 9. Checkpoint - Ensure all business logic tests pass
  - Run all unit and property tests for managers and data models
  - Verify test coverage meets 90% threshold for business logic
  - Ensure all tests pass, ask the user if questions arise

- [x] 10. Implement Streamlit UI foundation
  - [x] 10.1 Create main app structure and session initialization
    - Create app.py with Streamlit page configuration
    - Implement initialize_session() to set up user_id and navigation state
    - Implement apply_theme() with custom CSS for green soccer theme
    - Set up navigation state management in session
    - _Requirements: 7.1, 7.2, 7.3, 10.1, 10.3, 10.4_

  - [ ]* 10.2 Write property test for navigation context preservation
    - **Property 25: Navigation Context Preservation**
    - **Validates: Requirements 10.4**

  - [x] 10.3 Create home screen UI
    - Display "⚽ TIME KEEPER ⚽" title
    - Create three navigation buttons: Create Timer, Get Timer, Active Timers
    - Wire buttons to update session state for navigation
    - _Requirements: 7.2, 10.1, 10.3_

- [x] 11. Implement Create Timer screen
  - [x] 11.1 Build create timer UI and logic
    - Add back navigation button to home screen
    - Create text input for match description with validation
    - Create "Create Timer" button that calls MatchManager.create_match()
    - Display generated QR code using st.image() after creation
    - Display match UUID and formatted timer (01:30:00)
    - Display admin controls: Start, Pause, Reset, Stop buttons
    - Wire control buttons to TimerManager operations
    - Implement auto-refresh for running timer using st.rerun()
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.7, 5.8, 9.1, 9.2_

  - [ ]* 11.2 Write unit tests for create timer screen logic
    - Test match creation with valid description
    - Test QR code display after creation
    - Test timer control button actions
    - _Requirements: 1.1, 1.4, 5.2, 5.3, 5.4_

- [x] 12. Implement Get Timer screen
  - [x] 12.1 Build QR scanner and manual entry UI
    - Add back navigation button to home screen
    - Integrate streamlit-qrcode-scanner for QR scanning
    - Display error message if QR code cannot be decoded
    - Create text input for manual Match UUID entry
    - Implement UUID format validation before adding to match list
    - Display error if Match UUID does not exist in storage
    - Call UserManager.add_match_to_user() on successful scan/entry
    - Navigate to active timers screen after adding match
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 12.2 Write property test for non-existent match error
    - **Property 9: Non-Existent Match Error**
    - **Validates: Requirements 2.7**

  - [ ]* 12.3 Write unit tests for get timer screen logic
    - Test UUID validation with valid and invalid formats
    - Test error display for non-existent match
    - Test successful match addition to user list
    - _Requirements: 2.6, 2.7, 2.3_

- [x] 13. Implement Active Timers screen
  - [x] 13.1 Build match list display UI
    - Add back navigation button to home screen
    - Call UserManager.get_user_matches() to retrieve match UUIDs
    - Call MatchManager.list_active_matches() to get match details
    - Display each match with description, UUID, and formatted time remaining
    - Update time display every 1 second using st.rerun()
    - Add View button for each match to navigate to timer detail
    - Add Delete button for each match to remove from user's list
    - Implement delete functionality calling UserManager.remove_match_from_user()
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 10.2_

  - [ ]* 13.2 Write property test for match list display completeness
    - **Property 10: Match List Display Completeness**
    - **Validates: Requirements 3.1**

  - [ ]* 13.3 Write property test for match display information
    - **Property 11: Match Display Information**
    - **Validates: Requirements 3.2**

  - [ ]* 13.4 Write unit tests for active timers screen logic
    - Test match list retrieval and display
    - Test delete functionality removes match from list
    - Test time formatting in display
    - _Requirements: 3.1, 3.5, 3.3_

- [x] 14. Implement Timer Detail screen
  - [x] 14.1 Build timer detail UI with role-based controls
    - Add back navigation button to active timers screen
    - Display match description and UUID
    - Display large formatted timer with custom CSS styling
    - Call AccessControlManager.is_admin() to determine user role
    - For admin: display Pause/Resume, Reset, Stop control buttons
    - For spectator: display timer only without controls
    - Display status text (Running/Paused) and role indicator
    - Implement auto-refresh for running timer using st.rerun()
    - Call MatchManager.update_timer_display() to sync timer state
    - Wire control buttons to TimerManager operations and persist changes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.1, 6.2, 6.3, 8.5_

  - [ ]* 14.2 Write unit tests for timer detail screen logic
    - Test admin view displays all controls
    - Test spectator view hides controls
    - Test timer synchronization across page refreshes
    - _Requirements: 5.1, 6.1, 6.2, 8.5_

- [x] 15. Implement error handling and validation
  - [x] 15.1 Add comprehensive error handling across all components
    - Implement safe_load_match() with try-catch for storage errors
    - Implement safe_save_match() with permission and IO error handling
    - Implement safe_scan_qr_code() with scanner availability checks
    - Implement safe_generate_qr_code() with generation error handling
    - Implement safe_timer_operation() with state validation
    - Add user-facing error messages using st.error() and st.warning()
    - Add logging for debugging purposes
    - _Requirements: 2.4, 2.7, 8.1_

  - [ ]* 15.2 Write unit tests for error handling
    - Test storage error scenarios
    - Test QR code generation failures
    - Test invalid timer operations
    - _Requirements: 2.4, 8.1_

- [-] 16. Final integration and polish
  - [x] 16.1 Wire all components together and test end-to-end flows
    - Verify navigation flows between all screens
    - Test complete admin workflow: create → control → stop
    - Test complete spectator workflow: scan → view → follow
    - Verify timer synchronization across multiple users (manual test)
    - Verify QR codes scan correctly on mobile devices (manual test)
    - Ensure green theme is consistent across all screens
    - Test data persistence across page refreshes
    - _Requirements: 4.4, 5.6, 6.3, 7.1, 7.3, 8.4, 10.1, 10.2, 10.3, 10.4_

  - [ ]* 16.2 Write integration tests for complete workflows
    - Test admin creates match and controls timer
    - Test spectator scans QR and views match
    - Test multiple users viewing same match
    - _Requirements: 4.4, 5.6, 6.3_

- [x] 17. Final checkpoint - Ensure all tests pass and app is ready
  - Run complete test suite (unit, property, integration)
  - Verify 90% code coverage for business logic
  - Perform manual testing checklist for UI and mobile QR scanning
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation uses Python with Streamlit framework as specified in the design
- Timer synchronization uses timestamp-based calculation to maintain accuracy across page refreshes
- Storage uses JSON files with file locking for concurrent access
- QR codes are generated using the qrcode library and scanned using streamlit-qrcode-scanner
