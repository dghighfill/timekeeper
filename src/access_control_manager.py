"""Access control management for the Soccer Timekeeper App."""

from src.models import Match


class AccessControlManager:
    """Manages permission checks for match access and control."""
    
    def is_admin(self, user_id: str, match: Match) -> bool:
        """
        Checks if user is the admin of the match.
        
        Args:
            user_id: User ID to check
            match: Match object to check against
            
        Returns:
            bool: True if user_id matches match.admin_id, False otherwise
        """
        return user_id == match.admin_id
    
    def can_control_timer(self, user_id: str, match: Match) -> bool:
        """
        Checks if user can pause/resume/reset/stop timer.
        
        Only the admin of a match can control the timer.
        
        Args:
            user_id: User ID to check
            match: Match object to check against
            
        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.is_admin(user_id, match)
    
    def can_view_match(self, user_id: str, match: Match) -> bool:
        """
        Checks if user can view match details.
        
        All users can view any match (no restrictions on viewing).
        
        Args:
            user_id: User ID to check
            match: Match object to check against
            
        Returns:
            bool: Always True (all users can view matches)
        """
        return True
