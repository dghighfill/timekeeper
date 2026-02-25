"""Unit tests for timer detail screen functionality."""

import pytest
import uuid
from src.access_control_manager import AccessControlManager
from src.match_manager import MatchManager
from src.timer_manager import TimerManager
from src.storage_manager import StorageManager
from src.user_manager import UserManager


class TestTimerDetailScreenFunctionality:
    """Test suite for timer detail screen functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.storage_manager = StorageManager()
        self.timer_manager = TimerManager()
        self.match_manager = MatchManager(self.storage_manager, self.timer_manager)
        self.user_manager = UserManager(self.storage_manager)
        self.access_control = AccessControlManager()
    
    def test_access_control_admin_check(self):
        """Test that admin check works correctly."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Admin should have admin access
        assert self.access_control.is_admin(admin_id, match) == True
        
        # Other user should not have admin access
        other_user_id = f"user-{uuid.uuid4()}"
        assert self.access_control.is_admin(other_user_id, match) == False
    
    def test_access_control_can_control_timer(self):
        """Test that timer control permissions work correctly."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Admin should be able to control timer
        assert self.access_control.can_control_timer(admin_id, match) == True
        
        # Spectator should not be able to control timer
        spectator_id = f"spectator-{uuid.uuid4()}"
        assert self.access_control.can_control_timer(spectator_id, match) == False
    
    def test_access_control_can_view_match(self):
        """Test that all users can view matches."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Admin should be able to view
        assert self.access_control.can_view_match(admin_id, match) == True
        
        # Spectator should also be able to view
        spectator_id = f"spectator-{uuid.uuid4()}"
        assert self.access_control.can_view_match(spectator_id, match) == True
    
    def test_timer_operations_for_admin(self):
        """Test that admin can perform timer operations."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Verify admin can control timer
        assert self.access_control.can_control_timer(admin_id, match) == True
        
        # Test pause operation
        match.timer_state = self.timer_manager.pause(match.timer_state)
        assert match.timer_state.is_running == False
        
        # Test resume operation
        match.timer_state = self.timer_manager.resume(match.timer_state)
        assert match.timer_state.is_running == True
        
        # Test reset operation
        match.timer_state = self.timer_manager.reset(match.timer_state)
        assert match.timer_state.seconds_remaining == 5400
        assert match.timer_state.is_running == False
    
    def test_timer_display_update(self):
        """Test that timer display updates correctly."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Start the timer
        match.timer_state = self.timer_manager.resume(match.timer_state)
        self.match_manager.update_match(match)
        
        # Update timer display
        updated_match = self.match_manager.update_timer_display(match)
        
        # Timer should be updated
        assert updated_match is not None
        assert updated_match.timer_state.seconds_remaining <= 5400
    
    def test_stop_match_operation(self):
        """Test that stopping a match sets is_active to false."""
        # Create a match
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Test Match", admin_id)
        
        # Verify match is active
        assert match.is_active == True
        
        # Stop the match
        match.is_active = False
        self.match_manager.update_match(match)
        
        # Verify match is no longer active
        retrieved_match = self.match_manager.get_match(match.match_uuid)
        assert retrieved_match.is_active == False
    
    def test_timer_format_display(self):
        """Test that timer formatting works correctly."""
        # Test various time values
        test_cases = [
            (5400, "01:30:00"),  # 90 minutes
            (3600, "01:00:00"),  # 60 minutes
            (60, "00:01:00"),    # 1 minute
            (0, "00:00:00"),     # 0 seconds
            (3661, "01:01:01"),  # 1 hour, 1 minute, 1 second
        ]
        
        for seconds, expected_format in test_cases:
            formatted = self.timer_manager.format_time(seconds)
            assert formatted == expected_format
    
    def test_integration_admin_workflow(self):
        """Test complete admin workflow on timer detail screen."""
        # Create a match as admin
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Championship Final", admin_id)
        
        # Verify admin has control
        assert self.access_control.is_admin(admin_id, match) == True
        assert self.access_control.can_control_timer(admin_id, match) == True
        
        # Start timer
        match.timer_state = self.timer_manager.resume(match.timer_state)
        assert match.timer_state.is_running == True
        
        # Pause timer
        match.timer_state = self.timer_manager.pause(match.timer_state)
        assert match.timer_state.is_running == False
        
        # Resume timer
        match.timer_state = self.timer_manager.resume(match.timer_state)
        assert match.timer_state.is_running == True
        
        # Reset timer
        match.timer_state = self.timer_manager.reset(match.timer_state)
        assert match.timer_state.seconds_remaining == 5400
        assert match.timer_state.is_running == False
        
        # Stop match
        match.is_active = False
        self.match_manager.update_match(match)
        
        # Verify match is stopped
        retrieved_match = self.match_manager.get_match(match.match_uuid)
        assert retrieved_match.is_active == False
    
    def test_integration_spectator_workflow(self):
        """Test complete spectator workflow on timer detail screen."""
        # Create a match as admin
        admin_id = f"admin-{uuid.uuid4()}"
        match = self.match_manager.create_match("Championship Final", admin_id)
        
        # Add match to spectator's list
        spectator_id = f"spectator-{uuid.uuid4()}"
        self.user_manager.add_match_to_user(spectator_id, match.match_uuid)
        
        # Verify spectator can view but not control
        assert self.access_control.can_view_match(spectator_id, match) == True
        assert self.access_control.is_admin(spectator_id, match) == False
        assert self.access_control.can_control_timer(spectator_id, match) == False
        
        # Verify spectator can retrieve match
        retrieved_match = self.match_manager.get_match(match.match_uuid)
        assert retrieved_match is not None
        assert retrieved_match.match_uuid == match.match_uuid
        
        # Verify spectator's match list contains the match
        user_matches = self.user_manager.get_user_matches(spectator_id)
        assert match.match_uuid in user_matches
