"""
Analytics Models

Defines analytics and progress tracking database models.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, JSON, Float, Enum
# from sqlalchemy.dialects.postgresql import UUID  # Not compatible with SQLite
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class MetricType(enum.Enum):
    """Types of performance metrics"""
    SKILL_IMPROVEMENT = "skill_improvement"
    SIMULATION_PERFORMANCE = "simulation_performance"
    LEARNING_PROGRESS = "learning_progress"
    ENGAGEMENT = "engagement"
    GOAL_ADVANCEMENT = "goal_advancement"
    TIME_EFFICIENCY = "time_efficiency"


class AchievementType(enum.Enum):
    """Types of achievements"""
    SKILL_MASTERY = "skill_mastery"
    SIMULATION_COMPLETION = "simulation_completion"
    STREAK = "streak"
    MILESTONE = "milestone"
    IMPROVEMENT = "improvement"
    COMMUNITY = "community"


class TimeFrame(enum.Enum):
    """Time frame for analytics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class UserProgress(Base):
    """Comprehensive user progress tracking"""
    __tablename__ = "user_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Progress Summary
    overall_progress_score = Column(Float, default=0.0)  # 0.0-1.0
    skill_development_score = Column(Float, default=0.0)
    simulation_mastery_score = Column(Float, default=0.0)
    goal_achievement_score = Column(Float, default=0.0)
    
    # Learning Analytics
    total_learning_hours = Column(Float, default=0.0)
    sessions_completed = Column(Integer, default=0)
    simulations_completed = Column(Integer, default=0)
    skills_acquired = Column(Integer, default=0)
    
    # Performance Trends
    weekly_activity_score = Column(Float, default=0.0)
    improvement_velocity = Column(Float, default=0.0)  # Rate of improvement
    consistency_score = Column(Float, default=0.0)  # How consistent user is
    challenge_acceptance_rate = Column(Float, default=0.0)
    
    # Engagement Metrics
    platform_engagement_score = Column(Float, default=0.0)
    feature_usage_distribution = Column(JSON)  # Which features used most
    peak_activity_times = Column(JSON)  # When user is most active
    learning_streak_days = Column(Integer, default=0)
    
    # Predictive Analytics
    success_probability = Column(Float)  # Likelihood of achieving goals
    recommended_focus_areas = Column(JSON)  # AI recommendations
    risk_factors = Column(JSON)  # Factors that might impede progress
    optimization_suggestions = Column(JSON)  # How to improve faster
    
    # Comparative Data
    percentile_ranking = Column(Float)  # Compared to similar users
    peer_group_identifier = Column(String(100))  # Similar user cohort
    industry_benchmark_score = Column(Float)  # Compared to industry average
    
    # Time Period
    measurement_date = Column(DateTime(timezone=True), nullable=False)
    time_frame = Column(Enum(TimeFrame), default=TimeFrame.WEEKLY)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")


class PerformanceMetric(Base):
    """Individual performance metrics and measurements"""
    __tablename__ = "performance_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Metric Details
    metric_type = Column(Enum(MetricType), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))  # units, percentage, score, etc.
    
    # Context
    skill_name = Column(String(100))  # If skill-related
    simulation_id = Column(String(36))  # If simulation-related
    session_id = Column(String(36))  # If session-specific
    
    # Measurement Details
    measurement_method = Column(String(100))  # How it was measured
    confidence_level = Column(Float)  # Confidence in measurement (0.0-1.0)
    baseline_value = Column(Float)  # Previous/baseline measurement
    improvement_delta = Column(Float)  # Change from baseline
    
    # Target and Goals
    target_value = Column(Float)  # Target for this metric
    target_date = Column(DateTime(timezone=True))  # When target should be met
    is_target_met = Column(Boolean, default=False)
    
    # Analysis
    trend_direction = Column(String(20))  # improving, declining, stable
    trend_strength = Column(Float)  # How strong the trend is
    seasonality_factors = Column(JSON)  # Patterns in performance
    
    # External Factors
    contributing_factors = Column(JSON)  # What influenced this metric
    inhibiting_factors = Column(JSON)  # What held back performance
    
    # Quality and Reliability
    data_quality_score = Column(Float, default=1.0)
    outlier_flag = Column(Boolean, default=False)
    manual_override = Column(Boolean, default=False)
    
    # Timestamps
    measured_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Achievement(Base):
    """User achievements and milestones"""
    __tablename__ = "achievements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Achievement Details
    achievement_type = Column(Enum(AchievementType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    
    # Criteria
    criteria_met = Column(JSON)  # What criteria were satisfied
    threshold_value = Column(Float)  # Required value to achieve
    actual_value = Column(Float)  # User's actual value
    
    # Significance
    rarity_score = Column(Float)  # How rare this achievement is (0.0-1.0)
    difficulty_level = Column(String(20))  # easy, medium, hard, legendary
    points_awarded = Column(Integer, default=0)
    
    # Context
    skill_name = Column(String(100))  # If skill-related
    simulation_type = Column(String(50))  # If simulation-related
    goal_related = Column(Boolean, default=False)
    
    # Social Features
    is_shareable = Column(Boolean, default=True)
    congratulations_message = Column(Text)
    share_count = Column(Integer, default=0)
    
    # Progress Tracking
    progress_toward_next = Column(Float, default=0.0)  # Progress to next level
    next_level_requirements = Column(JSON)
    
    # Timestamps
    earned_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True))  # If achievement expires
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="achievements")
