# Requirements Document

## Introduction

The Soccer Timekeeper App is a Streamlit web application that enables match administrators to create and manage 90-minute soccer match timers, while allowing spectators to discover and follow matches through QR code scanning. The application provides role-based access control, real-time timer synchronization, and a soccer-themed user interface.

## Glossary

- **Application**: The Soccer Timekeeper Streamlit web application
- **Match**: A soccer game session with a unique identifier, description, and 90-minute timer
- **Admin**: The user who creates a Match and has control permissions
- **Spectator**: A user who scans a QR code to follow a Match but has view-only permissions
- **Match_UUID**: A unique identifier generated for each Match
- **QR_Code**: A scannable code containing the Match_UUID
- **Timer**: A countdown mechanism starting at 90 minutes (01:30:00 in HH:MM:SS format)
- **Match_List**: A collection of Matches that a user has added by scanning QR codes
- **Active_Match**: A Match that has not been stopped or deleted

## Requirements

### Requirement 1: Match Creation

**User Story:** As an admin, I want to create a new soccer match timer, so that I can track match time and share it with spectators.

#### Acceptance Criteria

1. WHEN an admin selects create timer, THE Application SHALL generate a unique Match_UUID
2. WHEN a Match_UUID is generated, THE Application SHALL create a QR_Code containing the Match_UUID
3. WHEN a Match is created, THE Application SHALL initialize the Timer to 90 minutes
4. WHEN a Match is created, THE Application SHALL store the Match with its Match_UUID, description, Timer state, and admin identifier
5. THE Application SHALL display the QR_Code on the create timer screen
6. THE Application SHALL display the Timer in HH:MM:SS format

### Requirement 2: QR Code Scanning

**User Story:** As a spectator, I want to scan a QR code, so that I can add a match to my list and follow its progress.

#### Acceptance Criteria

1. WHEN a user selects get timer, THE Application SHALL provide a QR code scanner interface
2. WHEN a QR_Code is scanned successfully, THE Application SHALL extract the Match_UUID
3. WHEN a Match_UUID is extracted, THE Application SHALL add the Match to the user's Match_List
4. IF a QR_Code cannot be decoded, THEN THE Application SHALL display an error message
5. WHERE QR scanning is unavailable, THE Application SHALL provide a text input field for manual Match_UUID entry
6. WHEN a Match_UUID is entered manually, THE Application SHALL validate the format before adding to Match_List
7. IF a Match_UUID does not exist in storage, THEN THE Application SHALL display an error message

### Requirement 3: Match List Display

**User Story:** As a user, I want to view all matches I've added, so that I can select and monitor specific matches.

#### Acceptance Criteria

1. WHEN a user selects active timers, THE Application SHALL display all Matches in the user's Match_List
2. FOR ALL Active_Matches in the list, THE Application SHALL display the description, Match_UUID, and current time remaining
3. THE Application SHALL display time remaining in HH:MM:SS format
4. THE Application SHALL provide a delete control for each Match in the list
5. WHEN a user deletes a Match, THE Application SHALL remove it from the user's Match_List
6. THE Application SHALL update the displayed time remaining at intervals of 1 second or less

### Requirement 4: Timer Countdown

**User Story:** As a user, I want to see the match time count down, so that I know how much time remains in the match.

#### Acceptance Criteria

1. WHILE a Timer is running, THE Application SHALL decrement the time by 1 second per second
2. WHEN the Timer reaches 00:00:00, THE Application SHALL stop decrementing
3. THE Application SHALL display the Timer in HH:MM:SS format with leading zeros
4. THE Application SHALL synchronize Timer state across all users viewing the same Match
5. WHILE a Timer is paused, THE Application SHALL maintain the current time value without decrementing

### Requirement 5: Admin Timer Controls

**User Story:** As an admin, I want to control the match timer, so that I can pause for injuries, reset for errors, or stop the match.

#### Acceptance Criteria

1. WHERE a user is the Admin of a Match, THE Application SHALL display pause, resume, reset, and stop controls
2. WHEN an Admin selects pause, THE Application SHALL stop the Timer from decrementing
3. WHEN an Admin selects resume, THE Application SHALL restart the Timer countdown
4. WHEN an Admin selects reset, THE Application SHALL set the Timer back to 90 minutes
5. WHEN an Admin selects stop, THE Application SHALL mark the Match as inactive
6. THE Application SHALL synchronize control actions across all users viewing the same Match
7. WHILE a Timer is running, THE Application SHALL display the pause control
8. WHILE a Timer is paused, THE Application SHALL display the resume control

### Requirement 6: Spectator View Restrictions

**User Story:** As a spectator, I want to view match time without controls, so that I can follow the match without accidentally interfering.

#### Acceptance Criteria

1. WHERE a user is not the Admin of a Match, THE Application SHALL display only the Timer and Match information
2. WHERE a user is not the Admin of a Match, THE Application SHALL hide pause, resume, reset, and stop controls
3. THE Application SHALL update the Timer display for Spectators in real-time as the Admin makes changes

### Requirement 7: Visual Theme

**User Story:** As a user, I want a soccer-themed interface, so that the app feels appropriate for soccer matches.

#### Acceptance Criteria

1. THE Application SHALL use shades of green as the primary color scheme
2. THE Application SHALL display "TIME KEEPER" as the home screen title
3. THE Application SHALL maintain consistent styling across all screens

### Requirement 8: Data Persistence

**User Story:** As a user, I want my match list and timer states to persist, so that I don't lose data when refreshing the page.

#### Acceptance Criteria

1. WHEN a Match is created, THE Application SHALL persist the Match data to storage
2. WHEN a Timer state changes, THE Application SHALL persist the updated state to storage
3. WHEN a user adds a Match to their Match_List, THE Application SHALL persist the association to storage
4. WHEN a user returns to the Application, THE Application SHALL load all persisted Match data and user associations
5. THE Application SHALL maintain Timer accuracy within 2 seconds after page refresh

### Requirement 9: QR Code Generation

**User Story:** As an admin, I want a QR code generated for my match, so that I can easily share it with spectators.

#### Acceptance Criteria

1. WHEN a Match is created, THE Application SHALL generate a QR_Code encoding the Match_UUID
2. THE Application SHALL display the QR_Code with sufficient size and contrast for mobile device scanning
3. THE QR_Code SHALL encode only the Match_UUID value
4. WHEN scanned by a standard QR code reader, THE QR_Code SHALL return the Match_UUID as a text string

### Requirement 10: Navigation

**User Story:** As a user, I want to navigate between screens, so that I can access different features of the application.

#### Acceptance Criteria

1. THE Application SHALL provide navigation controls for create timer, get timer, and active timers screens
2. WHEN a user selects a Match from the active timers list, THE Application SHALL navigate to the timer detail screen
3. THE Application SHALL provide a way to return to the home screen from any other screen
4. THE Application SHALL maintain user context when navigating between screens
