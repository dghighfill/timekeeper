"""Property-based tests for data persistence."""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
import tempfile
import os

from src.models import Match, TimerState
from src.storage_manager import StorageManager


# Hypothesis strategies for generating test data
def timer_states():
    """Generate valid TimerState instances."""
    return st.builds(
        TimerState,
        seconds_remaining=st.integers(min_value=0, max_value=5400),
        is_running=st.booleans(),
        last_update=st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2025, 12, 31)
        ),
        total_paused_time=st.integers(min_value=0, max_value=3600)
    )


def match_descriptions():
    """Generate valid match descriptions."""
    return st.text(
        alphabet=st.characters(
            blacklist_categories=('Cs', 'Cc'),
            blacklist_characters='\x00'
        ),
        min_size=1,
        max_size=200
    )


def matches():
    """Generate valid Match instances."""
    return st.builds(
        Match,
        match_uuid=st.uuids(version=4).map(str),
        description=match_descriptions(),
        admin_id=st.uuids(version=4).map(str),
        timer_state=timer_states(),
        created_at=st.datetimes(
            min_value=datetime(2024, 1, 1),
            max_value=datetime(2025, 12, 31)
        ),
        is_active=st.booleans()
    )


# Feature: soccer-timekeeper-app, Property 4: Match Persistence Round-Trip
# **Validates: Requirements 1.4, 8.1**
@given(matches())
def test_match_persistence_round_trip(match):
    """
    Property 4: For any match with valid data (UUID, description, timer state, admin ID),
    storing it and then loading it by UUID should return a match with identical field values.
    
    This validates that:
    - Match data is correctly serialized to storage
    - Match data is correctly deserialized from storage
    - All field values are preserved through the round-trip
    """
    # Create a temporary storage file for this test
    temp_dir = tempfile.mkdtemp()
    temp_storage_path = os.path.join(temp_dir, 'test_storage.json')
    
    try:
        # Create storage manager with temporary file
        storage = StorageManager(storage_path=temp_storage_path)
        
        # Save the match
        storage.save_match(match)
        
        # Load the match back
        loaded_match = storage.load_match(match.match_uuid)
        
        # Verify the match was loaded
        assert loaded_match is not None, "Match should be loaded from storage"
        
        # Verify all fields match
        assert loaded_match.match_uuid == match.match_uuid
        assert loaded_match.description == match.description
        assert loaded_match.admin_id == match.admin_id
        assert loaded_match.is_active == match.is_active
        
        # Verify created_at timestamp (allowing for microsecond precision loss in ISO format)
        assert abs((loaded_match.created_at - match.created_at).total_seconds()) < 0.001
        
        # Verify timer state fields
        assert loaded_match.timer_state.seconds_remaining == match.timer_state.seconds_remaining
        assert loaded_match.timer_state.is_running == match.timer_state.is_running
        assert loaded_match.timer_state.total_paused_time == match.timer_state.total_paused_time
        
        # Verify last_update timestamp (allowing for microsecond precision loss in ISO format)
        assert abs((loaded_match.timer_state.last_update - match.timer_state.last_update).total_seconds()) < 0.001
        
    finally:
        # Clean up temporary directory and file
        if os.path.exists(temp_storage_path):
            os.unlink(temp_storage_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


# Feature: soccer-timekeeper-app, Property 23: User Match List Persistence
# **Validates: Requirements 8.3**
@given(
    st.uuids(version=4).map(str),  # user_id
    st.lists(st.uuids(version=4).map(str), min_size=0, max_size=20)  # match_list
)
def test_user_match_list_persistence(user_id, match_list):
    """
    Property 23: For any user and match UUID, adding the match to the user's list,
    persisting, and then loading the user data should return a match list containing that UUID.

    This validates that:
    - User match lists are correctly serialized to storage
    - User match lists are correctly deserialized from storage
    - All match UUIDs in the list are preserved through the round-trip
    """
    # Create a temporary storage file for this test
    temp_dir = tempfile.mkdtemp()
    temp_storage_path = os.path.join(temp_dir, 'test_storage.json')

    try:
        # Create storage manager with temporary file
        storage = StorageManager(storage_path=temp_storage_path)

        # Save the user's match list
        storage.save_user_data(user_id, match_list)

        # Load the user's match list back
        loaded_match_list = storage.load_user_data(user_id)

        # Verify the match list was loaded correctly
        assert loaded_match_list is not None, "Match list should be loaded from storage"
        assert isinstance(loaded_match_list, list), "Loaded data should be a list"

        # Verify all match UUIDs are preserved
        assert len(loaded_match_list) == len(match_list), "Match list length should be preserved"
        assert loaded_match_list == match_list, "All match UUIDs should be preserved in order"

    finally:
        # Clean up temporary directory and file
        if os.path.exists(temp_storage_path):
            os.unlink(temp_storage_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)



# Feature: soccer-timekeeper-app, Property 23: User Match List Persistence
# **Validates: Requirements 8.3**
@given(
    st.uuids(version=4).map(str),  # user_id
    st.lists(st.uuids(version=4).map(str), min_size=0, max_size=20)  # match_list
)
def test_user_match_list_persistence(user_id, match_list):
    """
    Property 23: For any user and match UUID, adding the match to the user's list,
    persisting, and then loading the user data should return a match list containing that UUID.
    
    This validates that:
    - User match lists are correctly serialized to storage
    - User match lists are correctly deserialized from storage
    - All match UUIDs in the list are preserved through the round-trip
    """
    # Create a temporary storage file for this test
    temp_dir = tempfile.mkdtemp()
    temp_storage_path = os.path.join(temp_dir, 'test_storage.json')
    
    try:
        # Create storage manager with temporary file
        storage = StorageManager(storage_path=temp_storage_path)
        
        # Save the user's match list
        storage.save_user_data(user_id, match_list)
        
        # Load the user's match list back
        loaded_match_list = storage.load_user_data(user_id)
        
        # Verify the match list was loaded correctly
        assert loaded_match_list is not None, "Match list should be loaded from storage"
        assert isinstance(loaded_match_list, list), "Loaded data should be a list"
        
        # Verify all match UUIDs are preserved
        assert len(loaded_match_list) == len(match_list), "Match list length should be preserved"
        assert loaded_match_list == match_list, "All match UUIDs should be preserved in order"
        
    finally:
        # Clean up temporary directory and file
        if os.path.exists(temp_storage_path):
            os.unlink(temp_storage_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
