"""
Soccer Timekeeper App - Main Application
A Streamlit web application for managing soccer match timers with QR code sharing.
"""

import streamlit as st
import time
from config import Config
from src.user_manager import UserManager
from src.match_manager import MatchManager
from src.timer_manager import TimerManager
from src.qr_code_manager import QRCodeManager
from src.storage_manager import StorageManager


def initialize_session():
    """
    Initialize session state with user_id and navigation state.
    Sets up user identification and navigation context for the application.
    """
    # Initialize user_id if not present
    if 'user_id' not in st.session_state:
        user_manager = UserManager()
        st.session_state.user_id = user_manager.get_or_create_user_id()
    
    # Initialize navigation state
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = 'home'
    
    # Initialize selected match for detail view
    if 'selected_match' not in st.session_state:
        st.session_state.selected_match = None
    
    # Initialize created match UUID for create timer screen
    if 'created_match_uuid' not in st.session_state:
        st.session_state.created_match_uuid = None


def apply_theme():
    """
    Apply custom CSS for green soccer theme.
    Implements the visual theme requirements with green color scheme.
    """
    st.markdown(f"""
        <style>
        /* Global app styling */
        .stApp {{
            background-color: {Config.BACKGROUND_COLOR};
        }}
        
        /* Button styling */
        .stButton>button {{
            background-color: {Config.PRIMARY_COLOR};
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
            width: 100%;
            border: none;
            transition: background-color 0.3s;
        }}
        
        .stButton>button:hover {{
            background-color: {Config.TEXT_COLOR};
        }}
        
        /* Header styling */
        h1, h2, h3 {{
            color: {Config.TEXT_COLOR};
        }}
        
        /* Timer display styling */
        .timer-display {{
            font-size: 72px;
            font-weight: bold;
            color: {Config.PRIMARY_COLOR};
            text-align: center;
            padding: 40px;
            background-color: {Config.SECONDARY_COLOR};
            border-radius: 16px;
            font-family: 'Courier New', monospace;
        }}
        
        /* Title styling */
        .app-title {{
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: {Config.TEXT_COLOR};
            margin: 20px 0;
        }}
        
        /* Navigation button container */
        .nav-button {{
            margin: 10px 0;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_home_screen():
    """
    Render the home screen with navigation options.
    Displays title and three main navigation buttons.
    """
    # Display title
    st.markdown('<div class="app-title">⚽ TIME KEEPER ⚽</div>', unsafe_allow_html=True)
    
    st.write("")  # Add spacing
    st.write("")
    
    # Create navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎯 Create Timer", key="nav_create", use_container_width=True):
            st.session_state.current_screen = 'create_timer'
            st.session_state.created_match_uuid = None  # Reset created match
            st.rerun()
        
        st.write("")  # Spacing between buttons
        
        if st.button("📱 Get Timer", key="nav_get", use_container_width=True):
            st.session_state.current_screen = 'get_timer'
            st.rerun()
        
        st.write("")  # Spacing between buttons
        
        if st.button("📋 Active Timers", key="nav_active", use_container_width=True):
            st.session_state.current_screen = 'active_timers'
            st.rerun()


def render_create_timer_screen():
    """
    Render the create timer screen with match creation and admin controls.
    Allows admin to create a new match, displays QR code, and provides timer controls.
    """
    # Back navigation button
    if st.button("← Back to Home"):
        st.session_state.current_screen = 'home'
        st.session_state.created_match_uuid = None
        st.rerun()
    
    st.markdown("## Create New Match Timer")
    st.write("")
    
    # Initialize managers
    storage_manager = StorageManager()
    timer_manager = TimerManager()
    match_manager = MatchManager(storage_manager, timer_manager)
    qr_manager = QRCodeManager(box_size=Config.QR_BOX_SIZE, border=Config.QR_BORDER)
    
    # Match creation form (only show if no match created yet)
    if st.session_state.created_match_uuid is None:
        st.markdown("### Match Details")
        
        # Match description input with validation
        description = st.text_input(
            "Match Description:",
            placeholder="e.g., Championship Final",
            max_chars=200,
            key="match_description"
        )
        
        st.write("")
        
        # Create Timer button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Create Timer", key="create_match_btn", use_container_width=True):
                # Validate description
                if not description or description.strip() == "":
                    st.error("Match description cannot be empty.")
                else:
                    # Create the match
                    try:
                        match = match_manager.create_match(
                            description=description.strip(),
                            admin_id=st.session_state.user_id
                        )
                        st.session_state.created_match_uuid = match.match_uuid
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating match: {str(e)}")
    
    # Display match details and controls if match has been created
    if st.session_state.created_match_uuid is not None:
        # Load the match
        match = match_manager.get_match(st.session_state.created_match_uuid)
        
        if match is None:
            st.error("Match not found. Please try creating a new match.")
            st.session_state.created_match_uuid = None
            st.rerun()
            return
        
        # Update timer display based on elapsed time
        match = match_manager.update_timer_display(match)
        match_manager.update_match(match)
        
        st.markdown("---")
        st.markdown("### Match Created!")
        st.write("")
        
        # Display QR Code
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            qr_image = qr_manager.generate_qr_code(match.match_uuid)
            if qr_image:
                st.image(qr_image, caption="Scan to join match", use_container_width=True)
            else:
                st.error("Error generating QR code")
        
        st.write("")
        
        # Display Match ID
        st.markdown(f"**Match ID:** `{match.match_uuid}`")
        st.write("")
        
        # Display Timer
        formatted_time = timer_manager.format_time(match.timer_state.seconds_remaining)
        st.markdown(
            f'<div class="timer-display">{formatted_time}</div>',
            unsafe_allow_html=True
        )
        st.write("")
        
        # Admin Controls
        st.markdown("### Admin Controls")
        
        # Create control buttons based on timer state
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Start/Pause button
            if match.timer_state.is_running:
                if st.button("⏸ Pause", key="pause_btn", use_container_width=True):
                    match.timer_state = timer_manager.pause(match.timer_state)
                    match_manager.update_match(match)
                    st.rerun()
            else:
                if st.button("▶ Start", key="start_btn", use_container_width=True):
                    match.timer_state = timer_manager.resume(match.timer_state)
                    match_manager.update_match(match)
                    st.rerun()
        
        with col2:
            # Reset button
            if st.button("↻ Reset", key="reset_btn", use_container_width=True):
                match.timer_state = timer_manager.reset(match.timer_state)
                match_manager.update_match(match)
                st.rerun()
        
        with col3:
            # Stop button
            if st.button("⏹ Stop", key="stop_btn", use_container_width=True):
                match.is_active = False
                match_manager.update_match(match)
                st.success("Match stopped successfully!")
                time.sleep(1)
                st.session_state.created_match_uuid = None
                st.session_state.current_screen = 'home'
                st.rerun()
        
        st.write("")
        
        # Display status
        status = "Running" if match.timer_state.is_running else "Paused"
        st.markdown(f"**Status:** {status}")
        st.markdown("**Role:** Admin")
        
        # Auto-refresh for running timer
        if match.timer_state.is_running and match.timer_state.seconds_remaining > 0:
            time.sleep(Config.TIMER_UPDATE_INTERVAL)
            st.rerun()


def render_get_timer_screen():
    """
    Render the get timer screen with QR scanner and manual entry.
    Allows users to scan QR codes or manually enter Match UUIDs to add matches.
    """
    # Back navigation button
    if st.button("← Back to Home"):
        st.session_state.current_screen = 'home'
        st.rerun()
    
    st.markdown("## Scan QR Code to Add Match")
    st.write("")
    
    # Initialize managers
    storage_manager = StorageManager()
    timer_manager = TimerManager()
    match_manager = MatchManager(storage_manager, timer_manager)
    qr_manager = QRCodeManager(box_size=Config.QR_BOX_SIZE, border=Config.QR_BORDER)
    user_manager = UserManager(storage_manager)
    
    # QR Code Scanner Section
    st.markdown("### Scan QR Code")
    st.write("Use your device camera to scan a match QR code:")
    st.write("")
    
    try:
        from streamlit_qrcode_scanner import qrcode_scanner
        
        # Display QR scanner
        scan_result = qrcode_scanner(key='qr_scanner')
        
        if scan_result:
            # Extract and validate UUID from scan
            extracted_uuid = qr_manager.extract_uuid_from_scan(scan_result)
            
            if extracted_uuid:
                # Check if match exists in storage
                match = match_manager.get_match(extracted_uuid)
                
                if match:
                    # Add match to user's list
                    user_manager.add_match_to_user(st.session_state.user_id, extracted_uuid)
                    st.success(f"Match '{match.description}' added successfully!")
                    
                    # Navigate to active timers screen
                    time.sleep(1)
                    st.session_state.current_screen = 'active_timers'
                    st.rerun()
                else:
                    st.error("Match UUID does not exist in storage. Please check the QR code and try again.")
            else:
                st.error("QR code cannot be decoded. Please ensure the QR code is valid and try again.")
    
    except ImportError:
        st.warning("QR scanner is not available. Please use manual entry below.")
    except Exception as e:
        st.error(f"Error with QR scanner: {str(e)}. Please use manual entry below.")
    
    st.write("")
    st.markdown("---")
    st.write("")
    
    # Manual Entry Section
    st.markdown("### Or Enter Match ID Manually")
    st.write("If you have a Match ID, enter it below:")
    st.write("")
    
    # Manual UUID input
    manual_uuid = st.text_input(
        "Match ID:",
        placeholder="e.g., 550e8400-e29b-41d4-a716-446655440000",
        key="manual_uuid_input"
    )
    
    st.write("")
    
    # Add Match button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Add Match", key="add_match_btn", use_container_width=True):
            if not manual_uuid or manual_uuid.strip() == "":
                st.error("Please enter a Match ID.")
            else:
                # Validate UUID format
                if qr_manager.validate_uuid(manual_uuid.strip()):
                    # Check if match exists in storage
                    match = match_manager.get_match(manual_uuid.strip())
                    
                    if match:
                        # Add match to user's list
                        user_manager.add_match_to_user(st.session_state.user_id, manual_uuid.strip())
                        st.success(f"Match '{match.description}' added successfully!")
                        
                        # Navigate to active timers screen
                        time.sleep(1)
                        st.session_state.current_screen = 'active_timers'
                        st.rerun()
                    else:
                        st.error("Match UUID does not exist in storage. Please check the Match ID and try again.")
                else:
                    st.error("Invalid UUID format. Please enter a valid Match ID.")


def render_active_timers_screen():
    """
    Render the active timers screen with match list display.
    Displays all matches in the user's match list with time remaining and controls.
    """
    # Back navigation button
    if st.button("← Back to Home"):
        st.session_state.current_screen = 'home'
        st.rerun()
    
    st.markdown("## Your Active Matches")
    st.write("")
    
    # Initialize managers
    storage_manager = StorageManager()
    timer_manager = TimerManager()
    match_manager = MatchManager(storage_manager, timer_manager)
    user_manager = UserManager(storage_manager)
    
    # Get user's match list
    user_match_uuids = user_manager.get_user_matches(st.session_state.user_id)
    
    if not user_match_uuids:
        st.info("You haven't added any matches yet. Use 'Get Timer' to scan a QR code or enter a Match ID.")
        return
    
    # Get active matches
    active_matches = match_manager.list_active_matches(user_match_uuids)
    
    if not active_matches:
        st.info("No active matches found. All your matches may have ended.")
        return
    
    # Track if any timer is running for auto-refresh
    any_timer_running = False
    
    # Display each match
    for match in active_matches:
        # Update timer display based on elapsed time
        match = match_manager.update_timer_display(match)
        match_manager.update_match(match)
        
        # Check if this timer is running
        if match.timer_state.is_running and match.timer_state.seconds_remaining > 0:
            any_timer_running = True
        
        # Create a container for each match
        with st.container():
            st.markdown("---")
            
            # Match description
            st.markdown(f"### {match.description}")
            
            # Match ID
            st.markdown(f"**Match ID:** `{match.match_uuid}`")
            
            # Formatted time remaining
            formatted_time = timer_manager.format_time(match.timer_state.seconds_remaining)
            st.markdown(f"**Time Remaining:** {formatted_time}")
            
            # Status
            status = "Running" if match.timer_state.is_running else "Paused"
            st.markdown(f"**Status:** {status}")
            
            st.write("")
            
            # View and Delete buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("👁 View", key=f"view_{match.match_uuid}", use_container_width=True):
                    st.session_state.selected_match = match.match_uuid
                    st.session_state.current_screen = 'timer_detail'
                    st.rerun()
            
            with col2:
                if st.button("🗑 Delete", key=f"delete_{match.match_uuid}", use_container_width=True):
                    # Remove match from user's list
                    user_manager.remove_match_from_user(st.session_state.user_id, match.match_uuid)
                    st.success(f"Match '{match.description}' removed from your list.")
                    time.sleep(0.5)
                    st.rerun()
            
            st.write("")
    
    # Auto-refresh if any timer is running
    if any_timer_running:
        time.sleep(Config.TIMER_UPDATE_INTERVAL)
        st.rerun()


def render_timer_detail_screen():
    """
    Render the timer detail screen with role-based controls.
    Displays match timer with admin controls or spectator view based on user role.
    """
    # Back navigation button
    if st.button("← Back to Active Timers"):
        st.session_state.current_screen = 'active_timers'
        st.session_state.selected_match = None
        st.rerun()
    
    # Check if a match is selected
    if st.session_state.selected_match is None:
        st.error("No match selected. Please select a match from Active Timers.")
        return
    
    # Initialize managers
    storage_manager = StorageManager()
    timer_manager = TimerManager()
    match_manager = MatchManager(storage_manager, timer_manager)
    from src.access_control_manager import AccessControlManager
    access_control = AccessControlManager()
    
    # Load the selected match
    match = match_manager.get_match(st.session_state.selected_match)
    
    if match is None:
        st.error("Match not found. It may have been deleted.")
        st.session_state.selected_match = None
        return
    
    # Update timer display based on elapsed time
    match = match_manager.update_timer_display(match)
    match_manager.update_match(match)
    
    # Display match description
    st.markdown(f"## {match.description}")
    st.markdown(f"**Match ID:** `{match.match_uuid}`")
    st.write("")
    
    # Display large formatted timer
    formatted_time = timer_manager.format_time(match.timer_state.seconds_remaining)
    st.markdown(
        f'<div class="timer-display">{formatted_time}</div>',
        unsafe_allow_html=True
    )
    st.write("")
    
    # Check if user is admin
    is_admin = access_control.is_admin(st.session_state.user_id, match)
    
    # Display controls based on role
    if is_admin:
        st.markdown("### Admin Controls")
        
        # Create control buttons based on timer state
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pause/Resume button
            if match.timer_state.is_running:
                if st.button("⏸ Pause", key="detail_pause_btn", use_container_width=True):
                    match.timer_state = timer_manager.pause(match.timer_state)
                    match_manager.update_match(match)
                    st.rerun()
            else:
                if st.button("▶ Resume", key="detail_resume_btn", use_container_width=True):
                    match.timer_state = timer_manager.resume(match.timer_state)
                    match_manager.update_match(match)
                    st.rerun()
        
        with col2:
            # Reset button
            if st.button("↻ Reset", key="detail_reset_btn", use_container_width=True):
                match.timer_state = timer_manager.reset(match.timer_state)
                match_manager.update_match(match)
                st.rerun()
        
        with col3:
            # Stop button
            if st.button("⏹ Stop", key="detail_stop_btn", use_container_width=True):
                match.is_active = False
                match_manager.update_match(match)
                st.success("Match stopped successfully!")
                time.sleep(1)
                st.session_state.selected_match = None
                st.session_state.current_screen = 'active_timers'
                st.rerun()
        
        st.write("")
    
    # Display status and role
    status = "Running" if match.timer_state.is_running else "Paused"
    st.markdown(f"**Status:** {status}")
    
    if is_admin:
        st.markdown("**Role:** Admin")
    else:
        st.markdown("**Role:** Spectator")
    
    # Auto-refresh for running timer
    if match.timer_state.is_running and match.timer_state.seconds_remaining > 0:
        time.sleep(Config.TIMER_UPDATE_INTERVAL)
        st.rerun()


def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title="Soccer Timekeeper",
        page_icon="⚽",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session and apply theme
    initialize_session()
    apply_theme()
    
    # Route to appropriate screen based on navigation state
    current_screen = st.session_state.current_screen
    
    if current_screen == 'home':
        render_home_screen()
    elif current_screen == 'create_timer':
        render_create_timer_screen()
    elif current_screen == 'get_timer':
        render_get_timer_screen()
    elif current_screen == 'active_timers':
        render_active_timers_screen()
    elif current_screen == 'timer_detail':
        render_timer_detail_screen()


if __name__ == "__main__":
    main()
