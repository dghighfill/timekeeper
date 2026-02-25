"""Property-based tests for timer operations."""

import pytest
from hypothesis import given, strategies as st

from src.timer_manager import TimerManager


# Feature: soccer-timekeeper-app, Property 3: Timer Initialization
# **Validates: Requirements 1.3**
@given(st.integers(min_value=1, max_value=100))
def test_timer_initialization(num_initializations):
    """
    Property 3: For any newly created match, the timer should be initialized
    to exactly 5400 seconds (90 minutes).
    
    This validates that:
    - TimerManager.initialize_timer() always returns 5400 seconds
    - The timer is consistently initialized regardless of how many times it's called
    - The initialization is deterministic and correct
    """
    timer_manager = TimerManager()
    
    # Test multiple initializations to ensure consistency
    for _ in range(num_initializations):
        timer = timer_manager.initialize_timer()
        
        # Verify timer is initialized to exactly 90 minutes (5400 seconds)
        assert timer.seconds_remaining == 5400, \
            f"Timer should be initialized to 5400 seconds, got {timer.seconds_remaining}"
        
        # Verify timer is not running initially
        assert timer.is_running == False, \
            "Timer should not be running when initialized"
        
        # Verify total_paused_time is zero
        assert timer.total_paused_time == 0, \
            "Timer should have zero paused time when initialized"


# Feature: soccer-timekeeper-app, Property 5: Time Formatting
# **Validates: Requirements 1.6, 3.3, 4.3**
@given(st.integers(min_value=0, max_value=5400))
def test_time_formatting(seconds):
    """
    Property 5: For any integer value representing seconds (0 to 5400),
    the format function should produce a string matching the pattern HH:MM:SS
    with leading zeros, where HH is hours (00-01), MM is minutes (00-59),
    and SS is seconds (00-59).
    
    This validates that:
    - format_time produces strings in HH:MM:SS format
    - Leading zeros are present for all components
    - Hours are in range 00-01
    - Minutes are in range 00-59
    - Seconds are in range 00-59
    - The formatted time can be parsed back to the original seconds value
    """
    timer_manager = TimerManager()
    formatted = timer_manager.format_time(seconds)
    
    # Check format pattern: should be exactly 8 characters with colons at positions 2 and 5
    assert len(formatted) == 8, \
        f"Formatted time should be 8 characters, got {len(formatted)}: '{formatted}'"
    assert formatted[2] == ':', \
        f"Character at position 2 should be ':', got '{formatted[2]}'"
    assert formatted[5] == ':', \
        f"Character at position 5 should be ':', got '{formatted[5]}'"
    
    # Parse the components
    hours_str, minutes_str, secs_str = formatted.split(':')
    
    # Verify all components are digits
    assert hours_str.isdigit(), \
        f"Hours should be digits, got '{hours_str}'"
    assert minutes_str.isdigit(), \
        f"Minutes should be digits, got '{minutes_str}'"
    assert secs_str.isdigit(), \
        f"Seconds should be digits, got '{secs_str}'"
    
    # Verify leading zeros (all components should be 2 digits)
    assert len(hours_str) == 2, \
        f"Hours should have 2 digits with leading zero, got '{hours_str}'"
    assert len(minutes_str) == 2, \
        f"Minutes should have 2 digits with leading zero, got '{minutes_str}'"
    assert len(secs_str) == 2, \
        f"Seconds should have 2 digits with leading zero, got '{secs_str}'"
    
    # Convert to integers
    hours = int(hours_str)
    minutes = int(minutes_str)
    secs = int(secs_str)
    
    # Verify ranges
    assert 0 <= hours <= 1, \
        f"Hours should be 00-01, got {hours}"
    assert 0 <= minutes <= 59, \
        f"Minutes should be 00-59, got {minutes}"
    assert 0 <= secs <= 59, \
        f"Seconds should be 00-59, got {secs}"
    
    # Verify calculation: convert back to seconds and compare
    total = hours * 3600 + minutes * 60 + secs
    assert total == seconds, \
        f"Formatted time {formatted} should represent {seconds} seconds, but represents {total} seconds"
