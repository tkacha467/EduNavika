from typing import List, Optional
from pydantic import BaseModel, Field


class DailyGoalSummary(BaseModel):
    """Daily learning goal progress based on meaningful learning activities."""
    target: int = Field(5, description="Target daily meaningful activities")
    completed: int = Field(0, description="Completed meaningful activities today")
    percentage: float = Field(0.0, description="Goal completion percentage")
    is_completed: bool = Field(False, description="Whether daily goal is fulfilled")


class BadgeItem(BaseModel):
    """Individual achievement badge item with localized presentation."""
    badge_id: str = Field(..., description="Unique badge identifier")
    name: str = Field(..., description="Localized badge title")
    description: str = Field(..., description="Localized badge criteria description")
    icon: str = Field(..., description="Badge emoji/icon")
    is_unlocked: bool = Field(False, description="Whether badge is unlocked")
    unlocked_at: Optional[str] = Field(None, description="Timestamp or date when badge was unlocked")
    progress: int = Field(0, description="Current progress value")
    target: int = Field(1, description="Target value required to unlock")


class GamificationResponse(BaseModel):
    """Comprehensive gamification profile for student dashboard."""
    student_id: str = Field(..., description="Student profile ID")
    total_xp: int = Field(0, description="Total empirical experience points earned")
    level: int = Field(1, description="Current student level (1-5)")
    level_title: str = Field(..., description="Localized title for current level")
    xp_towards_next_level: int = Field(0, description="XP earned towards next level threshold")
    xp_required_for_next_level: int = Field(100, description="XP span required to reach next level")
    level_progress_percentage: float = Field(0.0, description="Progress percentage towards next level")
    current_streak: int = Field(0, description="Active consecutive learning days")
    longest_streak: int = Field(0, description="Longest consecutive learning days recorded")
    last_learning_date: Optional[str] = Field(None, description="Date of last meaningful activity (YYYY-MM-DD)")
    streak_active_today: bool = Field(False, description="True if student has completed an activity today")
    daily_goal: DailyGoalSummary = Field(..., description="Today's learning goal status")
    unlocked_badges: List[BadgeItem] = Field(default_factory=list, description="Unlocked achievement badges")
    locked_badges: List[BadgeItem] = Field(default_factory=list, description="Locked achievement badges")
    recently_earned_badges: List[BadgeItem] = Field(default_factory=list, description="Recently unlocked badges")
