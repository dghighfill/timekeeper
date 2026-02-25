# Design Document: Soccer Timekeeper App

## Overview

The Soccer Timekeeper App is a Streamlit-based web application that provides real-time match timer management with role-based access control. The system enables match administrators to create 90-minute soccer match timers and share them via QR codes, while spectators can scan these codes to follow matches in real-time.

The application architecture follows a client-server model where Streamlit handles both the UI rendering and server-side state management. The design emphasizes real-time synchronization, persistent storage, and a clear separation between admin and spectator capabilities.

Key technical challenges addressed:
- Real-time timer synchronization across multiple concurrent users
- Role-based access control without traditional authentication
- QR code generation and scanning within a web application
- Persistent state management across page refreshes
- Sub-second UI updates in Streamlit's request-response model

## Architecture

### System Architecture

The application follows a three-tier architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│                  (Streamlit UI Components)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Home    │  │  Create  │  │   Get    │             │
│  │  Screen  │  │  Timer   │  │  Timer   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐                            │
│  │  Active  │  │  Timer   │                            │
│  │  Timers  │  │  Detail  │                            │
│  └──────────┘  └──────────┘                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Business Logic Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Match     │  │    Timer     │  │   QR Code    │ │
│  │   Manager    │  │   Manager    │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐                   │
│  │     User     │  │    Access    │                   │
│  │   Manager    │  │   Control    │                   │
│  └──────────────┘  └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Match      │  │    User      │  │   Session    │ │
│  │   Storage    │  │   Storage    │  │   Storage    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│              (JSON files or SQLite)                     │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend Framework**: Streamlit (Python-based web framework)
- **QR Code Generation**: `qrcode` library with PIL for image generation
- **QR Code Scanning**: `streamlit-qrcode-scanner` or `opencv-python` with `pyzbar`
- **Data Persistence**: JSON files or SQLite database
- **Session Management**: Streamlit session state
- **UUID Generation**: Python `uuid` library
- **Styling**: Streamlit custom CSS for green soccer theme

### Deployment Model

The application runs as a single Streamlit server instance. For production:
- Deploy on Streamlit Cloud, Heroku, or AWS EC2
- Use file-based storage (JSON) for simple deployments
- Consider SQLite or PostgreSQL for multi-instance deployments
- Implement file locking or database transactions for concurrent access

## Components and Interfaces

### 1. Match Manager

Responsible for creating, retrieving, updating, and deleting matches.

```python
class MatchManager:
    def create_match(self, description: str, admin_id: str) -> Match:
        """Creates a new match with UUID, initializes timer to 90 minutes"""
        
    def get_match(self, match_uuid: str) -> Optional[Match]:
        """Retrieves a match by UUID"""
        
    def update_match(self, match: Match) -> None:
        """Persists match state changes"""
        
    def delete_match(self, match_uuid: str) -> None:
        """Marks match as inactive"""
        
    def list_active_matches(self, match_uuids: List[str]) -> List[Match]:
        """Returns all active matches for given UUIDs"""
```

### 2. Timer Manager

Handles timer state transitions and countdown logic.

```python
class TimerManager:
    def initialize_timer(self) -> TimerState:
        """Creates timer at 90 minutes (5400 seconds)"""
        
    def tick(self, timer: TimerState) -> TimerState:
        """Decrements timer by 1 second if running and > 0"""
        
    def pause(self, timer: TimerState) -> TimerState:
        """Pauses the timer"""
        
    def resume(self, timer: TimerState) -> TimerState:
        """Resumes the timer"""
        
    def reset(self, timer: TimerState) -> TimerState:
        """Resets timer to 90 minutes"""
        
    def format_time(self, seconds: int) -> str:
        """Formats seconds as HH:MM:SS with leading zeros"""
        
    def get_elapsed_time(self, timer: TimerState) -> int:
        """Calculates actual elapsed time accounting for pauses"""
```

### 3. QR Code Manager

Generates and validates QR codes containing match UUIDs.

```python
class QRCodeManager:
    def generate_qr_code(self, match_uuid: str) -> Image:
        """Generates QR code image encoding the match UUID"""
        
    def validate_uuid(self, uuid_string: str) -> bool:
        """Validates UUID format"""
        
    def extract_uuid_from_scan(self, scan_result: str) -> Optional[str]:
        """Extracts and validates UUID from scanned data"""
```

### 4. User Manager

Manages user sessions and match lists.

```python
class UserManager:
    def get_or_create_user_id(self) -> str:
        """Gets user ID from session or creates new one"""
        
    def add_match_to_user(self, user_id: str, match_uuid: str) -> None:
        """Adds match UUID to user's match list"""
        
    def remove_match_from_user(self, user_id: str, match_uuid: str) -> None:
        """Removes match UUID from user's match list"""
        
    def get_user_matches(self, user_id: str) -> List[str]:
        """Returns list of match UUIDs for user"""
```

### 5. Access Control Manager

Determines user permissions for matches.

```python
class AccessControlManager:
    def is_admin(self, user_id: str, match: Match) -> bool:
        """Checks if user is the admin of the match"""
        
    def can_control_timer(self, user_id: str, match: Match) -> bool:
        """Checks if user can pause/resume/reset/stop timer"""
        
    def can_view_match(self, user_id: str, match: Match) -> bool:
        """Checks if user can view match details"""
```

### 6. Storage Manager

Handles data persistence operations.

```python
class StorageManager:
    def save_match(self, match: Match) -> None:
        """Persists match data to storage"""
        
    def load_match(self, match_uuid: str) -> Optional[Match]:
        """Loads match data from storage"""
        
    def save_user_data(self, user_id: str, match_list: List[str]) -> None:
        """Persists user's match list"""
        
    def load_user_data(self, user_id: str) -> List[str]:
        """Loads user's match list"""
        
    def list_all_matches(self) -> List[Match]:
        """Returns all matches in storage"""
```

## Data Models

### Match

```python
@dataclass
class Match:
    match_uuid: str          # UUID v4 string
    description: str         # User-provided match description
    admin_id: str           # User ID of the creator
    timer_state: TimerState # Current timer state
    created_at: datetime    # Match creation timestamp
    is_active: bool         # Whether match is active
```

### TimerState

```python
@dataclass
class TimerState:
    seconds_remaining: int   # Time remaining in seconds (0-5400)
    is_running: bool        # Whether timer is currently counting down
    last_update: datetime   # Timestamp of last state change
    total_paused_time: int  # Cumulative paused time in seconds
```

### User

```python
@dataclass
class User:
    user_id: str            # Unique user identifier (stored in session)
    match_list: List[str]   # List of match UUIDs user is following
```

### Storage Schema

For JSON-based storage:

```json
{
  "matches": {
    "uuid-1": {
      "match_uuid": "uuid-1",
      "description": "Championship Final",
      "admin_id": "user-123",
      "timer_state": {
        "seconds_remaining": 5400,
        "is_running": true,
        "last_update": "2024-01-15T10:30:00Z",
        "total_paused_time": 0
      },
      "created_at": "2024-01-15T10:00:00Z",
      "is_active": true
    }
  },
  "users": {
    "user-123": {
      "user_id": "user-123",
      "match_list": ["uuid-1", "uuid-2"]
    }
  }
}
```


## UI Component Design

### Home Screen

```
┌─────────────────────────────────────────┐
│          ⚽ TIME KEEPER ⚽               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      🎯 Create Timer              │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      📱 Get Timer                 │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │      📋 Active Timers             │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Create Timer Screen

```
┌─────────────────────────────────────────┐
│  ← Back to Home                         │
│                                         │
│  Create New Match Timer                 │
│                                         │
│  Match Description:                     │
│  [_____________________________]        │
│                                         │
│  [Create Timer]                         │
│                                         │
│  ─────────────────────────────          │
│  Match Created!                         │
│                                         │
│  ┌─────────────────┐                   │
│  │                 │                   │
│  │   QR CODE       │                   │
│  │                 │                   │
│  └─────────────────┘                   │
│                                         │
│  Match ID: abc-123-def                 │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      01:30:00                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [▶ Start] [⏸ Pause] [↻ Reset] [⏹ Stop]│
│                                         │
└─────────────────────────────────────────┘
```

### Get Timer Screen

```
┌─────────────────────────────────────────┐
│  ← Back to Home                         │
│                                         │
│  Scan QR Code to Add Match              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │    [Camera View/Scanner]        │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Or enter Match ID manually:            │
│  [_____________________________]        │
│  [Add Match]                            │
│                                         │
└─────────────────────────────────────────┘
```

### Active Timers Screen

```
┌─────────────────────────────────────────┐
│  ← Back to Home                         │
│                                         │
│  Your Active Matches                    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Championship Final              │   │
│  │ ID: abc-123-def                 │   │
│  │ Time: 01:25:43                  │   │
│  │ [View] [Delete]                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Practice Match                  │   │
│  │ ID: xyz-789-ghi                 │   │
│  │ Time: 00:45:12                  │   │
│  │ [View] [Delete]                 │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

### Timer Detail Screen (Admin View)

```
┌─────────────────────────────────────────┐
│  ← Back to Active Timers                │
│                                         │
│  Championship Final                     │
│  Match ID: abc-123-def                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │        01:25:43                 │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [⏸ Pause] [↻ Reset] [⏹ Stop]          │
│                                         │
│  Status: Running                        │
│  You are the admin                      │
│                                         │
└─────────────────────────────────────────┘
```

### Timer Detail Screen (Spectator View)

```
┌─────────────────────────────────────────┐
│  ← Back to Active Timers                │
│                                         │
│  Championship Final                     │
│  Match ID: abc-123-def                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │        01:25:43                 │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Status: Running                        │
│  Spectator view                         │
│                                         │
└─────────────────────────────────────────┘
```

## Implementation Details

### Real-Time Timer Synchronization

Challenge: Streamlit's request-response model doesn't natively support real-time updates.

Solution:
1. Use `st.rerun()` with a small delay to create a polling loop
2. Store timer state with `last_update` timestamp
3. On each render, calculate elapsed time since `last_update`
4. Update `seconds_remaining` based on elapsed time if timer is running
5. Persist updated state to storage

```python
def update_timer_display(match: Match) -> Match:
    """Updates timer based on elapsed time since last update"""
    if match.timer_state.is_running:
        now = datetime.now()
        elapsed = (now - match.timer_state.last_update).total_seconds()
        new_remaining = max(0, match.timer_state.seconds_remaining - int(elapsed))
        
        match.timer_state.seconds_remaining = new_remaining
        match.timer_state.last_update = now
        
        if new_remaining == 0:
            match.timer_state.is_running = False
    
    return match
```

### Session Management

Use Streamlit's session state to maintain:
- User ID (generated on first visit, persisted in session)
- Current screen/navigation state
- Selected match UUID for detail view

```python
def initialize_session():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = 'home'
    if 'selected_match' not in st.session_state:
        st.session_state.selected_match = None
```

### QR Code Implementation

Generation:
```python
import qrcode
from PIL import Image

def generate_qr_code(match_uuid: str) -> Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(match_uuid)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")
```

Scanning:
```python
from streamlit_qrcode_scanner import qrcode_scanner

def scan_qr_code():
    result = qrcode_scanner(key='qr_scanner')
    if result:
        return extract_uuid(result)
    return None
```

### Storage Implementation

JSON-based storage with file locking for concurrent access:

```python
import json
import fcntl
from pathlib import Path

class JSONStorage:
    def __init__(self, storage_path: str = "data/storage.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        
    def _read_with_lock(self) -> dict:
        with open(self.storage_path, 'r+') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return data
    
    def _write_with_lock(self, data: dict) -> None:
        with open(self.storage_path, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(data, f, indent=2, default=str)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### Styling Implementation

Apply custom CSS for green soccer theme:

```python
def apply_theme():
    st.markdown("""
        <style>
        .stApp {
            background-color: #e8f5e9;
        }
        .stButton>button {
            background-color: #2e7d32;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #1b5e20;
        }
        h1, h2, h3 {
            color: #1b5e20;
        }
        .timer-display {
            font-size: 72px;
            font-weight: bold;
            color: #2e7d32;
            text-align: center;
            padding: 40px;
            background-color: #c8e6c9;
            border-radius: 16px;
            font-family: 'Courier New', monospace;
        }
        </style>
    """, unsafe_allow_html=True)
```

### Auto-Refresh Implementation

Implement automatic page refresh for timer updates:

```python
import time

def auto_refresh_timer(interval: float = 1.0):
    """Refreshes page at specified interval for timer updates"""
    time.sleep(interval)
    st.rerun()

# In main app loop
if st.session_state.current_screen == 'timer_detail':
    match = get_current_match()
    if match and match.timer_state.is_running:
        auto_refresh_timer(1.0)
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:

- Properties 1.6, 3.3, and 4.3 all test HH:MM:SS formatting - consolidated into one property
- Properties 1.2, 9.1, and 9.4 all test QR code round-trip - consolidated into one property
- Properties 6.1 and 6.2 both test spectator view restrictions - consolidated into one property
- Properties 1.4 and 8.1 both test match persistence - consolidated into one property
- Property 8.4 is covered by the combination of other persistence properties

The following properties provide unique validation value and will be implemented:

### Property 1: UUID Uniqueness

*For any* sequence of match creations, all generated Match_UUIDs should be unique with no duplicates.

**Validates: Requirements 1.1**

### Property 2: QR Code Round-Trip

*For any* valid Match_UUID, generating a QR code and then decoding it should return the exact same UUID value with no additional data.

**Validates: Requirements 1.2, 2.2, 9.1, 9.3, 9.4**

### Property 3: Timer Initialization

*For any* newly created match, the timer should be initialized to exactly 5400 seconds (90 minutes).

**Validates: Requirements 1.3**

### Property 4: Match Persistence Round-Trip

*For any* match with valid data (UUID, description, timer state, admin ID), storing it and then loading it by UUID should return a match with identical field values.

**Validates: Requirements 1.4, 8.1**

### Property 5: Time Formatting

*For any* integer value representing seconds (0 to 5400), the format function should produce a string matching the pattern HH:MM:SS with leading zeros, where HH is hours (00-01), MM is minutes (00-59), and SS is seconds (00-59).

**Validates: Requirements 1.6, 3.3, 4.3**

### Property 6: Match List Addition

*For any* user and any valid Match_UUID, adding the match to the user's list should result in that UUID appearing in the user's match list when retrieved.

**Validates: Requirements 2.3**

### Property 7: Invalid QR Code Handling

*For any* invalid or corrupted QR code data, the decode function should return an error result rather than crashing or returning invalid data.

**Validates: Requirements 2.4**

### Property 8: UUID Format Validation

*For any* string input, the UUID validation function should return true only for strings that match the UUID v4 format (8-4-4-4-12 hexadecimal pattern).

**Validates: Requirements 2.6**

### Property 9: Non-Existent Match Error

*For any* Match_UUID that does not exist in storage, attempting to load it should return None or an error indicator rather than invalid data.

**Validates: Requirements 2.7**

### Property 10: Match List Display Completeness

*For any* user with a non-empty match list, retrieving active matches should return all matches whose UUIDs are in the user's list and whose is_active flag is true.

**Validates: Requirements 3.1**

### Property 11: Match Display Information

*For any* active match, the rendered display data should include the match description, Match_UUID, and formatted time remaining.

**Validates: Requirements 3.2**

### Property 12: Match List Deletion

*For any* user and any Match_UUID in their match list, removing the match should result in that UUID no longer appearing in the user's match list when retrieved.

**Validates: Requirements 3.5**

### Property 13: Timer Countdown

*For any* timer in running state with seconds_remaining > 0, advancing time by N seconds should decrease seconds_remaining by N seconds (or to 0 if N exceeds remaining time).

**Validates: Requirements 4.1**

### Property 14: Timer Zero Boundary

*For any* timer with seconds_remaining = 0, calling tick should leave seconds_remaining at 0 and set is_running to false (idempotent at boundary).

**Validates: Requirements 4.2**

### Property 15: Paused Timer Idempotence

*For any* timer in paused state (is_running = false), calling tick should not change seconds_remaining.

**Validates: Requirements 4.5**

### Property 16: Pause Action

*For any* timer in running state, executing pause should set is_running to false while preserving seconds_remaining.

**Validates: Requirements 5.2**

### Property 17: Resume Action

*For any* timer in paused state, executing resume should set is_running to true while preserving seconds_remaining.

**Validates: Requirements 5.3**

### Property 18: Reset Action

*For any* timer in any state, executing reset should set seconds_remaining to 5400 and is_running to false.

**Validates: Requirements 5.4**

### Property 19: Stop Action

*For any* match in active state, executing stop should set is_active to false.

**Validates: Requirements 5.5**

### Property 20: Admin Control Visibility

*For any* user who is the admin of a match (user_id matches match.admin_id), the UI should include pause/resume, reset, and stop controls.

**Validates: Requirements 5.1, 5.7, 5.8**

### Property 21: Spectator View Restrictions

*For any* user who is not the admin of a match (user_id does not match match.admin_id), the UI should not include pause, resume, reset, or stop controls.

**Validates: Requirements 6.1, 6.2**

### Property 22: Timer State Persistence

*For any* timer state change (pause, resume, reset), persisting the match and then loading it should return a timer with the updated state values.

**Validates: Requirements 8.2**

### Property 23: User Match List Persistence

*For any* user and match UUID, adding the match to the user's list, persisting, and then loading the user data should return a match list containing that UUID.

**Validates: Requirements 8.3**

### Property 24: Timer Accuracy After Reload

*For any* running timer with a last_update timestamp, recalculating seconds_remaining based on elapsed time should produce a value within 2 seconds of the expected countdown.

**Validates: Requirements 8.5**

### Property 25: Navigation Context Preservation

*For any* navigation action between screens, the user's session data (user_id and match_list) should remain unchanged before and after navigation.

**Validates: Requirements 10.4**


## Error Handling

### Error Categories

1. **User Input Errors**
   - Invalid Match UUID format
   - Empty match description
   - Malformed QR code data

2. **Storage Errors**
   - File system access failures
   - JSON parsing errors
   - Concurrent access conflicts

3. **State Errors**
   - Attempting to access non-existent match
   - Invalid timer state transitions
   - Session data corruption

4. **System Errors**
   - QR code generation failures
   - Camera/scanner unavailable
   - Network issues (if deployed with remote storage)

### Error Handling Strategy

#### User Input Validation

```python
def validate_match_uuid(uuid_string: str) -> tuple[bool, Optional[str]]:
    """
    Validates UUID format.
    Returns: (is_valid, error_message)
    """
    try:
        uuid.UUID(uuid_string, version=4)
        return (True, None)
    except ValueError:
        return (False, "Invalid UUID format. Please check and try again.")

def validate_match_description(description: str) -> tuple[bool, Optional[str]]:
    """
    Validates match description.
    Returns: (is_valid, error_message)
    """
    if not description or description.strip() == "":
        return (False, "Match description cannot be empty.")
    if len(description) > 200:
        return (False, "Match description must be 200 characters or less.")
    return (True, None)
```

#### Storage Error Handling

```python
def safe_load_match(match_uuid: str) -> Optional[Match]:
    """
    Safely loads match with error handling.
    Returns None if match doesn't exist or error occurs.
    """
    try:
        return storage_manager.load_match(match_uuid)
    except FileNotFoundError:
        st.error(f"Match {match_uuid} not found.")
        return None
    except json.JSONDecodeError:
        st.error("Storage data is corrupted. Please contact support.")
        return None
    except Exception as e:
        st.error(f"Unexpected error loading match: {str(e)}")
        return None

def safe_save_match(match: Match) -> bool:
    """
    Safely saves match with error handling.
    Returns True if successful, False otherwise.
    """
    try:
        storage_manager.save_match(match)
        return True
    except PermissionError:
        st.error("Cannot save match. Check file permissions.")
        return False
    except Exception as e:
        st.error(f"Error saving match: {str(e)}")
        return False
```

#### QR Code Error Handling

```python
def safe_scan_qr_code() -> Optional[str]:
    """
    Safely scans QR code with error handling.
    Returns UUID string if successful, None otherwise.
    """
    try:
        result = qrcode_scanner(key='qr_scanner')
        if result:
            is_valid, error = validate_match_uuid(result)
            if is_valid:
                return result
            else:
                st.error(error)
                return None
    except Exception as e:
        st.warning("QR scanner unavailable. Please use manual entry.")
        return None

def safe_generate_qr_code(match_uuid: str) -> Optional[Image]:
    """
    Safely generates QR code with error handling.
    Returns Image if successful, None otherwise.
    """
    try:
        return qr_manager.generate_qr_code(match_uuid)
    except Exception as e:
        st.error(f"Error generating QR code: {str(e)}")
        return None
```

#### State Error Handling

```python
def safe_timer_operation(match: Match, operation: str) -> Optional[Match]:
    """
    Safely performs timer operation with validation.
    Returns updated match if successful, None otherwise.
    """
    if not match.is_active:
        st.error("Cannot modify inactive match.")
        return None
    
    try:
        if operation == "pause":
            match.timer_state = timer_manager.pause(match.timer_state)
        elif operation == "resume":
            match.timer_state = timer_manager.resume(match.timer_state)
        elif operation == "reset":
            match.timer_state = timer_manager.reset(match.timer_state)
        elif operation == "stop":
            match.is_active = False
        else:
            st.error(f"Unknown operation: {operation}")
            return None
        
        if safe_save_match(match):
            return match
        return None
    except Exception as e:
        st.error(f"Error performing {operation}: {str(e)}")
        return None
```

### User-Facing Error Messages

All error messages should be:
- Clear and actionable
- Non-technical for end users
- Displayed using Streamlit's error/warning components
- Logged for debugging purposes

Example messages:
- "Match not found. Please check the Match ID and try again."
- "QR code could not be read. Please try again or enter the Match ID manually."
- "Unable to save changes. Please check your connection and try again."
- "This match has ended and cannot be modified."

## Testing Strategy

### Overview

The testing strategy employs a dual approach combining unit tests for specific scenarios and property-based tests for comprehensive validation of universal properties. This ensures both concrete correctness and general robustness across all possible inputs.

### Testing Framework

- **Unit Testing**: pytest
- **Property-Based Testing**: Hypothesis (Python property-based testing library)
- **Test Configuration**: Minimum 100 iterations per property test
- **Coverage Target**: 90% code coverage for business logic

### Property-Based Testing Implementation

Each correctness property from the design will be implemented as a Hypothesis test with appropriate generators and assertions.

#### Example Property Test Structure

```python
from hypothesis import given, strategies as st
import pytest

# Feature: soccer-timekeeper-app, Property 1: UUID Uniqueness
@given(st.lists(st.integers(min_value=1, max_value=100), min_size=2, max_size=100))
def test_uuid_uniqueness(num_matches):
    """
    Property 1: For any sequence of match creations, 
    all generated Match_UUIDs should be unique.
    """
    match_manager = MatchManager()
    uuids = []
    
    for i in range(len(num_matches)):
        match = match_manager.create_match(
            description=f"Match {i}",
            admin_id="test_admin"
        )
        uuids.append(match.match_uuid)
    
    # All UUIDs should be unique
    assert len(uuids) == len(set(uuids))

# Feature: soccer-timekeeper-app, Property 2: QR Code Round-Trip
@given(st.uuids(version=4))
def test_qr_code_round_trip(match_uuid):
    """
    Property 2: For any valid Match_UUID, generating a QR code 
    and then decoding it should return the exact same UUID.
    """
    qr_manager = QRCodeManager()
    uuid_str = str(match_uuid)
    
    # Generate QR code
    qr_image = qr_manager.generate_qr_code(uuid_str)
    
    # Decode QR code
    decoded_uuid = qr_manager.decode_qr_code(qr_image)
    
    # Should get back exact same UUID
    assert decoded_uuid == uuid_str

# Feature: soccer-timekeeper-app, Property 5: Time Formatting
@given(st.integers(min_value=0, max_value=5400))
def test_time_formatting(seconds):
    """
    Property 5: For any integer value representing seconds (0 to 5400),
    the format function should produce HH:MM:SS with leading zeros.
    """
    timer_manager = TimerManager()
    formatted = timer_manager.format_time(seconds)
    
    # Check format pattern
    assert len(formatted) == 8
    assert formatted[2] == ':' and formatted[5] == ':'
    
    # Parse back to verify correctness
    hours, minutes, secs = formatted.split(':')
    assert all(part.isdigit() for part in [hours, minutes, secs])
    assert 0 <= int(hours) <= 1
    assert 0 <= int(minutes) <= 59
    assert 0 <= int(secs) <= 59
    
    # Verify calculation
    total = int(hours) * 3600 + int(minutes) * 60 + int(secs)
    assert total == seconds

# Feature: soccer-timekeeper-app, Property 13: Timer Countdown
@given(
    st.integers(min_value=1, max_value=5400),
    st.integers(min_value=1, max_value=100)
)
def test_timer_countdown(initial_seconds, elapsed_seconds):
    """
    Property 13: For any timer in running state, advancing time by N seconds
    should decrease seconds_remaining by N (or to 0 if N exceeds remaining).
    """
    timer_manager = TimerManager()
    timer = TimerState(
        seconds_remaining=initial_seconds,
        is_running=True,
        last_update=datetime.now(),
        total_paused_time=0
    )
    
    expected_remaining = max(0, initial_seconds - elapsed_seconds)
    
    # Simulate elapsed time
    for _ in range(elapsed_seconds):
        timer = timer_manager.tick(timer)
    
    assert timer.seconds_remaining == expected_remaining
```

### Unit Testing Strategy

Unit tests complement property tests by focusing on:

1. **Specific Examples**: Concrete scenarios that demonstrate correct behavior
2. **Edge Cases**: Boundary conditions and special cases
3. **Integration Points**: Component interactions and data flow
4. **Error Conditions**: Specific error scenarios and recovery

#### Example Unit Tests

```python
def test_create_match_with_valid_description():
    """Example: Creating a match with valid description succeeds"""
    match_manager = MatchManager()
    match = match_manager.create_match("Championship Final", "admin_123")
    
    assert match.description == "Championship Final"
    assert match.admin_id == "admin_123"
    assert match.timer_state.seconds_remaining == 5400
    assert match.is_active == True

def test_timer_at_zero_stops():
    """Edge case: Timer at 0 should not go negative"""
    timer_manager = TimerManager()
    timer = TimerState(
        seconds_remaining=0,
        is_running=True,
        last_update=datetime.now(),
        total_paused_time=0
    )
    
    timer = timer_manager.tick(timer)
    
    assert timer.seconds_remaining == 0
    assert timer.is_running == False

def test_invalid_uuid_format_rejected():
    """Error condition: Invalid UUID format should be rejected"""
    qr_manager = QRCodeManager()
    
    is_valid = qr_manager.validate_uuid("not-a-valid-uuid")
    
    assert is_valid == False

def test_spectator_cannot_control_timer():
    """Access control: Spectator should not have control permissions"""
    access_control = AccessControlManager()
    match = Match(
        match_uuid="test-uuid",
        description="Test Match",
        admin_id="admin_123",
        timer_state=TimerState(...),
        created_at=datetime.now(),
        is_active=True
    )
    
    can_control = access_control.can_control_timer("spectator_456", match)
    
    assert can_control == False
```

### Test Organization

```
tests/
├── unit/
│   ├── test_match_manager.py
│   ├── test_timer_manager.py
│   ├── test_qr_code_manager.py
│   ├── test_user_manager.py
│   ├── test_access_control.py
│   └── test_storage_manager.py
├── property/
│   ├── test_properties_match.py
│   ├── test_properties_timer.py
│   ├── test_properties_qr.py
│   ├── test_properties_persistence.py
│   └── test_properties_access.py
├── integration/
│   ├── test_match_lifecycle.py
│   ├── test_user_workflows.py
│   └── test_storage_integration.py
└── conftest.py  # Shared fixtures and configuration
```

### Test Data Generators (Hypothesis Strategies)

```python
from hypothesis import strategies as st
from datetime import datetime, timedelta

# Generate valid match descriptions
match_descriptions = st.text(
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
    min_size=1,
    max_size=200
)

# Generate timer states
timer_states = st.builds(
    TimerState,
    seconds_remaining=st.integers(min_value=0, max_value=5400),
    is_running=st.booleans(),
    last_update=st.datetimes(
        min_value=datetime.now() - timedelta(hours=2),
        max_value=datetime.now()
    ),
    total_paused_time=st.integers(min_value=0, max_value=3600)
)

# Generate matches
matches = st.builds(
    Match,
    match_uuid=st.uuids(version=4).map(str),
    description=match_descriptions,
    admin_id=st.uuids(version=4).map(str),
    timer_state=timer_states,
    created_at=st.datetimes(
        min_value=datetime.now() - timedelta(days=1),
        max_value=datetime.now()
    ),
    is_active=st.booleans()
)
```

### Continuous Integration

- Run all tests on every commit
- Enforce minimum 90% coverage for business logic
- Property tests run with 100 iterations in CI
- Integration tests run against temporary storage
- Performance benchmarks for timer accuracy

### Manual Testing Checklist

In addition to automated tests, manual testing should verify:

- [ ] QR codes scan correctly on mobile devices
- [ ] UI displays correctly on different screen sizes
- [ ] Timer updates appear smooth and responsive
- [ ] Green theme is visually appealing and consistent
- [ ] Navigation flows are intuitive
- [ ] Error messages are clear and helpful
- [ ] Multiple users can view same match simultaneously
- [ ] Page refresh preserves state correctly

## Deployment Considerations

### Environment Setup

```bash
# Required Python packages
streamlit>=1.28.0
qrcode[pil]>=7.4.2
streamlit-qrcode-scanner>=0.1.0
hypothesis>=6.92.0
pytest>=7.4.0
```

### Configuration

```python
# config.py
import os

class Config:
    # Storage
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'data/storage.json')
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'json')  # 'json' or 'sqlite'
    
    # Timer
    MATCH_DURATION_SECONDS = 5400  # 90 minutes
    TIMER_UPDATE_INTERVAL = 1.0    # seconds
    TIMER_ACCURACY_THRESHOLD = 2   # seconds
    
    # UI
    PRIMARY_COLOR = '#2e7d32'      # Green
    BACKGROUND_COLOR = '#e8f5e9'   # Light green
    
    # QR Code
    QR_BOX_SIZE = 10
    QR_BORDER = 4
```

### Production Deployment

For Streamlit Cloud:
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#2e7d32"
backgroundColor = "#e8f5e9"
secondaryBackgroundColor = "#c8e6c9"
textColor = "#1b5e20"

[server]
enableCORS = false
enableXsrfProtection = true
```

### Monitoring and Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Match created: {match_uuid}")
logger.warning(f"Invalid UUID attempt: {invalid_uuid}")
logger.error(f"Storage error: {error_message}")
```

## Future Enhancements

Potential features for future iterations:

1. **Multi-Period Support**: Support for halftime and extra time periods
2. **Match History**: Archive completed matches with statistics
3. **Notifications**: Push notifications for match events
4. **Authentication**: Optional user accounts for persistent identity
5. **Match Sharing**: Share match links via social media
6. **Customizable Duration**: Support for different match lengths
7. **Stoppage Time**: Add injury/stoppage time tracking
8. **Multiple Timers**: Run multiple independent timers simultaneously
9. **Analytics**: Track match statistics and viewing patterns
10. **Mobile App**: Native mobile applications for iOS/Android

