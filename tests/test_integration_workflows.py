"""
Integration tests for end-to-end workflows in the Soccer Timekeeper App.
Tests complete user journeys including admin and spectator workflows.
"""

import pytest
import time
from datetime import datetime
from src.match_manager import MatchManager
from src.timer_manager import TimerManager
from src.qr_code_manager import QRCodeManager
from src.user_manager import UserManager
from src.storage_manager import StorageManager
from src.access_control_manager import AccessControlManager


class TestAdminWorkflow:
    """Test complete admin workflow: create → control → stop"""
    
    def test_admin_creates_and_controls_match(self, tmp_path):
        """
        Test the complete admin workflow:
        1. Admin creates a match
        2. Admin starts the timer
        3. Admin pauses the timer
        4. Admin resumes the timer
        5. Admin resets the timer
        6. Admin stops the match
        """
        # Setup
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        access_control = AccessControlManager()
        admin_id = "admin_user_123"
        
        # Step 1: Admin creates a match
        match = match_manager.create_match(
            description="Championship Final",
            admin_id=admin_id
        )
        
        assert match is not None
        assert match.description == "Championship Final"
        assert match.admin_id == admin_id
        assert match.timer_state.seconds_remaining == 5400
        assert match.timer_state.is_running is False
        assert match.is_active is True
        
        # Verify admin has control permissions
        assert access_control.is_admin(admin_id, match) is True
        assert access_control.can_control_timer(admin_id, match) is True
        
        # Step 2: Admin starts the timer
        match.timer_state = timer_manager.resume(match.timer_state)
        match_manager.update_match(match)
        
        assert match.timer_state.is_running is True
        
        # Simulate some time passing (at least 1 second for timer to decrement)
        time.sleep(1.1)
        match = match_manager.update_timer_display(match)
        
        # Timer should have decremented (within reasonable bounds)
        assert match.timer_state.seconds_remaining < 5400
        assert match.timer_state.seconds_remaining >= 5398  # Should be around 5399 or 5398
        
        # Step 3: Admin pauses the timer
        paused_time = match.timer_state.seconds_remaining
        match.timer_state = timer_manager.pause(match.timer_state)
        match_manager.update_match(match)
        
        assert match.timer_state.is_running is False
        
        # Simulate time passing while paused (timer should not change)
        time.sleep(0.5)
        match = match_manager.update_timer_display(match)
        
        # Timer should not have changed while paused
        assert match.timer_state.seconds_remaining == paused_time
        
        # Step 4: Admin resumes the timer
        match.timer_state = timer_manager.resume(match.timer_state)
        match_manager.update_match(match)
        
        assert match.timer_state.is_running is True
        
        # Step 5: Admin resets the timer
        match.timer_state = timer_manager.reset(match.timer_state)
        match_manager.update_match(match)
        
        assert match.timer_state.seconds_remaining == 5400
        assert match.timer_state.is_running is False
        
        # Step 6: Admin stops the match
        match.is_active = False
        match_manager.update_match(match)
        
        assert match.is_active is False
        
        # Verify match is persisted correctly
        loaded_match = match_manager.get_match(match.match_uuid)
        assert loaded_match is not None
        assert loaded_match.is_active is False


class TestSpectatorWorkflow:
    """Test complete spectator workflow: scan → view → follow"""
    
    def test_spectator_scans_and_follows_match(self, tmp_path):
        """
        Test the complete spectator workflow:
        1. Admin creates a match and generates QR code
        2. Spectator scans QR code (simulated by extracting UUID)
        3. Spectator adds match to their list
        4. Spectator views match details
        5. Spectator follows match updates
        6. Spectator removes match from their list
        """
        # Setup
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        qr_manager = QRCodeManager()
        user_manager = UserManager(storage_manager)
        access_control = AccessControlManager()
        
        admin_id = "admin_user_123"
        spectator_id = "spectator_user_456"
        
        # Step 1: Admin creates a match and generates QR code
        match = match_manager.create_match(
            description="Practice Match",
            admin_id=admin_id
        )
        
        qr_image = qr_manager.generate_qr_code(match.match_uuid)
        assert qr_image is not None
        
        # Step 2: Spectator scans QR code (simulated)
        # In real scenario, this would be decoded from the QR image
        scanned_uuid = match.match_uuid
        
        # Validate the scanned UUID
        assert qr_manager.validate_uuid(scanned_uuid) is True
        
        # Step 3: Spectator adds match to their list
        user_manager.add_match_to_user(spectator_id, scanned_uuid)
        
        # Verify match is in spectator's list
        spectator_matches = user_manager.get_user_matches(spectator_id)
        assert scanned_uuid in spectator_matches
        
        # Step 4: Spectator views match details
        viewed_match = match_manager.get_match(scanned_uuid)
        assert viewed_match is not None
        assert viewed_match.description == "Practice Match"
        
        # Verify spectator does not have control permissions
        assert access_control.is_admin(spectator_id, viewed_match) is False
        assert access_control.can_control_timer(spectator_id, viewed_match) is False
        
        # Step 5: Spectator follows match updates
        # Admin starts the timer
        viewed_match.timer_state = timer_manager.resume(viewed_match.timer_state)
        match_manager.update_match(viewed_match)
        
        # Spectator refreshes and sees updated timer (wait at least 1 second)
        time.sleep(1.1)
        spectator_view = match_manager.get_match(scanned_uuid)
        spectator_view = match_manager.update_timer_display(spectator_view)
        
        assert spectator_view.timer_state.is_running is True
        assert spectator_view.timer_state.seconds_remaining < 5400
        assert spectator_view.timer_state.seconds_remaining >= 5398  # Should be around 5399 or 5398
        
        # Step 6: Spectator removes match from their list
        user_manager.remove_match_from_user(spectator_id, scanned_uuid)
        
        # Verify match is no longer in spectator's list
        spectator_matches = user_manager.get_user_matches(spectator_id)
        assert scanned_uuid not in spectator_matches


class TestNavigationFlows:
    """Test navigation flows between all screens"""
    
    def test_navigation_preserves_user_context(self, tmp_path):
        """
        Test that navigation between screens preserves user context:
        - User ID remains consistent
        - Match list is maintained
        - Selected match is preserved
        """
        # Setup
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        user_manager = UserManager(storage_manager)
        
        user_id = "test_user_789"
        
        # Create some matches
        match1 = match_manager.create_match("Match 1", "admin_1")
        match2 = match_manager.create_match("Match 2", "admin_2")
        
        # Add matches to user's list
        user_manager.add_match_to_user(user_id, match1.match_uuid)
        user_manager.add_match_to_user(user_id, match2.match_uuid)
        
        # Verify user context before navigation
        initial_matches = user_manager.get_user_matches(user_id)
        assert len(initial_matches) == 2
        assert match1.match_uuid in initial_matches
        assert match2.match_uuid in initial_matches
        
        # Simulate navigation by reloading user data
        # (In real app, this happens when switching screens)
        reloaded_matches = user_manager.get_user_matches(user_id)
        
        # Verify user context is preserved
        assert reloaded_matches == initial_matches
        assert len(reloaded_matches) == 2
        
        # Verify match data is still accessible
        reloaded_match1 = match_manager.get_match(match1.match_uuid)
        reloaded_match2 = match_manager.get_match(match2.match_uuid)
        
        assert reloaded_match1 is not None
        assert reloaded_match2 is not None
        assert reloaded_match1.description == "Match 1"
        assert reloaded_match2.description == "Match 2"


class TestDataPersistence:
    """Test data persistence across page refreshes"""
    
    def test_match_state_persists_across_reload(self, tmp_path):
        """
        Test that match state persists correctly:
        1. Create a match and start timer
        2. Simulate page refresh by creating new manager instances
        3. Verify timer state is preserved
        """
        storage_path = str(tmp_path / "test_storage.json")
        
        # Initial session
        storage_manager1 = StorageManager(storage_path=storage_path)
        timer_manager1 = TimerManager()
        match_manager1 = MatchManager(storage_manager1, timer_manager1)
        
        # Create and start a match
        match = match_manager1.create_match("Persistent Match", "admin_123")
        match.timer_state = timer_manager1.resume(match.timer_state)
        match_manager1.update_match(match)
        
        # Wait a bit for timer to run (at least 1 second)
        time.sleep(1.1)
        match = match_manager1.update_timer_display(match)
        match_manager1.update_match(match)
        
        saved_time = match.timer_state.seconds_remaining
        saved_running_state = match.timer_state.is_running
        match_uuid = match.match_uuid
        
        # Simulate page refresh - create new manager instances
        storage_manager2 = StorageManager(storage_path=storage_path)
        timer_manager2 = TimerManager()
        match_manager2 = MatchManager(storage_manager2, timer_manager2)
        
        # Load the match
        reloaded_match = match_manager2.get_match(match_uuid)
        
        assert reloaded_match is not None
        assert reloaded_match.description == "Persistent Match"
        assert reloaded_match.admin_id == "admin_123"
        assert reloaded_match.is_active is True
        
        # Update timer display to account for elapsed time
        reloaded_match = match_manager2.update_timer_display(reloaded_match)
        
        # Timer should be running and have decremented
        assert reloaded_match.timer_state.is_running == saved_running_state
        # Timer accuracy should be within 2 seconds (as per requirements)
        assert abs(reloaded_match.timer_state.seconds_remaining - saved_time) <= 2
    
    def test_user_match_list_persists_across_reload(self, tmp_path):
        """
        Test that user match lists persist correctly:
        1. User adds matches to their list
        2. Simulate page refresh by creating new manager instances
        3. Verify match list is preserved
        """
        storage_path = str(tmp_path / "test_storage.json")
        
        # Initial session
        storage_manager1 = StorageManager(storage_path=storage_path)
        timer_manager1 = TimerManager()
        match_manager1 = MatchManager(storage_manager1, timer_manager1)
        user_manager1 = UserManager(storage_manager1)
        
        user_id = "persistent_user_123"
        
        # Create matches and add to user's list
        match1 = match_manager1.create_match("Match A", "admin_1")
        match2 = match_manager1.create_match("Match B", "admin_2")
        match3 = match_manager1.create_match("Match C", "admin_3")
        
        user_manager1.add_match_to_user(user_id, match1.match_uuid)
        user_manager1.add_match_to_user(user_id, match2.match_uuid)
        user_manager1.add_match_to_user(user_id, match3.match_uuid)
        
        # Simulate page refresh - create new manager instances
        storage_manager2 = StorageManager(storage_path=storage_path)
        user_manager2 = UserManager(storage_manager2)
        
        # Load user's match list
        reloaded_matches = user_manager2.get_user_matches(user_id)
        
        assert len(reloaded_matches) == 3
        assert match1.match_uuid in reloaded_matches
        assert match2.match_uuid in reloaded_matches
        assert match3.match_uuid in reloaded_matches


class TestTimerSynchronization:
    """Test timer synchronization across multiple users"""
    
    def test_multiple_users_see_same_timer_state(self, tmp_path):
        """
        Test that multiple users viewing the same match see synchronized timer:
        1. Admin creates and starts a match
        2. Multiple spectators view the match
        3. All users see the same timer state
        4. Admin pauses timer
        5. All users see paused state
        """
        storage_path = str(tmp_path / "test_storage.json")
        
        # Admin creates match
        admin_storage = StorageManager(storage_path=storage_path)
        admin_timer_mgr = TimerManager()
        admin_match_mgr = MatchManager(admin_storage, admin_timer_mgr)
        
        match = admin_match_mgr.create_match("Synchronized Match", "admin_123")
        match.timer_state = admin_timer_mgr.resume(match.timer_state)
        admin_match_mgr.update_match(match)
        
        # Wait a bit (at least 1 second for timer to decrement)
        time.sleep(1.1)
        match = admin_match_mgr.update_timer_display(match)
        admin_match_mgr.update_match(match)
        
        admin_time = match.timer_state.seconds_remaining
        match_uuid = match.match_uuid
        
        # Spectator 1 views match
        spectator1_storage = StorageManager(storage_path=storage_path)
        spectator1_timer_mgr = TimerManager()
        spectator1_match_mgr = MatchManager(spectator1_storage, spectator1_timer_mgr)
        
        spectator1_match = spectator1_match_mgr.get_match(match_uuid)
        spectator1_match = spectator1_match_mgr.update_timer_display(spectator1_match)
        
        # Spectator 2 views match
        spectator2_storage = StorageManager(storage_path=storage_path)
        spectator2_timer_mgr = TimerManager()
        spectator2_match_mgr = MatchManager(spectator2_storage, spectator2_timer_mgr)
        
        spectator2_match = spectator2_match_mgr.get_match(match_uuid)
        spectator2_match = spectator2_match_mgr.update_timer_display(spectator2_match)
        
        # All users should see similar timer values (within 2 seconds)
        assert abs(spectator1_match.timer_state.seconds_remaining - admin_time) <= 2
        assert abs(spectator2_match.timer_state.seconds_remaining - admin_time) <= 2
        assert abs(spectator1_match.timer_state.seconds_remaining - spectator2_match.timer_state.seconds_remaining) <= 2
        
        # All users should see running state
        assert spectator1_match.timer_state.is_running is True
        assert spectator2_match.timer_state.is_running is True
        
        # Admin pauses timer
        match.timer_state = admin_timer_mgr.pause(match.timer_state)
        admin_match_mgr.update_match(match)
        
        # Spectators reload and see paused state
        spectator1_match = spectator1_match_mgr.get_match(match_uuid)
        spectator2_match = spectator2_match_mgr.get_match(match_uuid)
        
        assert spectator1_match.timer_state.is_running is False
        assert spectator2_match.timer_state.is_running is False


class TestMatchListDisplay:
    """Test match list display functionality"""
    
    def test_active_matches_filtered_correctly(self, tmp_path):
        """
        Test that only active matches are displayed:
        1. Create multiple matches
        2. Stop some matches
        3. Verify only active matches are returned
        """
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        user_manager = UserManager(storage_manager)
        
        user_id = "test_user_123"
        
        # Create matches
        match1 = match_manager.create_match("Active Match 1", "admin_1")
        match2 = match_manager.create_match("Active Match 2", "admin_2")
        match3 = match_manager.create_match("Inactive Match", "admin_3")
        
        # Add all matches to user's list
        user_manager.add_match_to_user(user_id, match1.match_uuid)
        user_manager.add_match_to_user(user_id, match2.match_uuid)
        user_manager.add_match_to_user(user_id, match3.match_uuid)
        
        # Stop match3
        match3.is_active = False
        match_manager.update_match(match3)
        
        # Get active matches
        user_match_uuids = user_manager.get_user_matches(user_id)
        active_matches = match_manager.list_active_matches(user_match_uuids)
        
        # Should only return active matches
        assert len(active_matches) == 2
        active_uuids = [m.match_uuid for m in active_matches]
        assert match1.match_uuid in active_uuids
        assert match2.match_uuid in active_uuids
        assert match3.match_uuid not in active_uuids
    
    def test_match_display_includes_required_information(self, tmp_path):
        """
        Test that match display includes all required information:
        - Description
        - Match UUID
        - Formatted time remaining
        """
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        
        # Create a match
        match = match_manager.create_match("Display Test Match", "admin_123")
        
        # Verify all required information is present
        assert match.description == "Display Test Match"
        assert match.match_uuid is not None
        assert len(match.match_uuid) > 0
        
        # Verify time can be formatted
        formatted_time = timer_manager.format_time(match.timer_state.seconds_remaining)
        assert formatted_time == "01:30:00"
        assert len(formatted_time) == 8
        assert formatted_time.count(':') == 2


class TestQRCodeWorkflow:
    """Test QR code generation and scanning workflow"""
    
    def test_qr_code_round_trip_workflow(self, tmp_path):
        """
        Test complete QR code workflow:
        1. Admin creates match
        2. QR code is generated
        3. QR code contains correct UUID
        4. UUID can be validated
        5. Match can be retrieved using UUID
        """
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        qr_manager = QRCodeManager()
        
        # Step 1: Admin creates match
        match = match_manager.create_match("QR Test Match", "admin_123")
        match_uuid = match.match_uuid
        
        # Step 2: QR code is generated
        qr_image = qr_manager.generate_qr_code(match_uuid)
        assert qr_image is not None
        
        # Step 3: Simulate scanning (in real scenario, would decode from image)
        scanned_uuid = match_uuid  # Simulated scan result
        
        # Step 4: UUID can be validated
        is_valid = qr_manager.validate_uuid(scanned_uuid)
        assert is_valid is True
        
        # Step 5: Match can be retrieved using UUID
        retrieved_match = match_manager.get_match(scanned_uuid)
        assert retrieved_match is not None
        assert retrieved_match.match_uuid == match_uuid
        assert retrieved_match.description == "QR Test Match"


class TestErrorHandling:
    """Test error handling in workflows"""
    
    def test_invalid_match_uuid_handling(self, tmp_path):
        """Test that invalid match UUIDs are handled gracefully"""
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        qr_manager = QRCodeManager()
        
        # Test invalid UUID format
        invalid_uuid = "not-a-valid-uuid"
        assert qr_manager.validate_uuid(invalid_uuid) is False
        
        # Test non-existent but valid UUID format
        import uuid
        non_existent_uuid = str(uuid.uuid4())
        match = match_manager.get_match(non_existent_uuid)
        assert match is None
    
    def test_empty_match_description_handling(self, tmp_path):
        """Test that empty match descriptions are handled"""
        storage_manager = StorageManager(storage_path=str(tmp_path / "test_storage.json"))
        timer_manager = TimerManager()
        match_manager = MatchManager(storage_manager, timer_manager)
        
        # Empty description should still create match (validation happens in UI)
        match = match_manager.create_match("", "admin_123")
        assert match is not None
        assert match.description == ""
