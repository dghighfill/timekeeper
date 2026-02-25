"""Timer management for the Soccer Timekeeper App."""

from datetime import datetime
from src.models import TimerState


class TimerManager:
    """Manages timer operations for soccer matches."""
    
    MATCH_DURATION_SECONDS = 5400  # 90 minutes
    
    def initialize_timer(self) -> TimerState:
        """
        Creates a new timer initialized to 90 minutes (5400 seconds).
        
        Returns:
            TimerState: A new timer at 5400 seconds, not running
        """
        return TimerState(
            seconds_remaining=self.MATCH_DURATION_SECONDS,
            is_running=False,
            last_update=datetime.now(),
            total_paused_time=0
        )
    
    def tick(self, timer: TimerState) -> TimerState:
        """
        Decrements timer by 1 second if running and > 0.
        
        Args:
            timer: Current timer state
            
        Returns:
            TimerState: Updated timer state
        """
        if timer.is_running and timer.seconds_remaining > 0:
            timer.seconds_remaining -= 1
            timer.last_update = datetime.now()
            
            # Stop timer when it reaches zero
            if timer.seconds_remaining == 0:
                timer.is_running = False
        
        return timer
    
    def pause(self, timer: TimerState) -> TimerState:
        """
        Pauses the timer.
        
        Args:
            timer: Current timer state
            
        Returns:
            TimerState: Timer with is_running set to False
        """
        timer.is_running = False
        timer.last_update = datetime.now()
        return timer
    
    def resume(self, timer: TimerState) -> TimerState:
        """
        Resumes the timer.
        
        Args:
            timer: Current timer state
            
        Returns:
            TimerState: Timer with is_running set to True
        """
        timer.is_running = True
        timer.last_update = datetime.now()
        return timer
    
    def reset(self, timer: TimerState) -> TimerState:
        """
        Resets timer to 90 minutes and stops it.
        
        Args:
            timer: Current timer state
            
        Returns:
            TimerState: Timer reset to 5400 seconds, not running
        """
        timer.seconds_remaining = self.MATCH_DURATION_SECONDS
        timer.is_running = False
        timer.last_update = datetime.now()
        timer.total_paused_time = 0
        return timer
    
    def format_time(self, seconds: int) -> str:
        """
        Formats seconds as HH:MM:SS with leading zeros.
        
        Args:
            seconds: Time in seconds (0-5400)
            
        Returns:
            str: Formatted time string (e.g., "01:30:00")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_elapsed_time(self, timer: TimerState) -> int:
        """
        Calculates actual elapsed time accounting for pauses.
        
        Args:
            timer: Current timer state
            
        Returns:
            int: Elapsed time in seconds
        """
        total_time = self.MATCH_DURATION_SECONDS
        time_used = total_time - timer.seconds_remaining
        return time_used
