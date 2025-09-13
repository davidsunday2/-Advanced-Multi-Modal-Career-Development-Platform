"""
Career Models

Defines career-related database models including goals, learning paths, and job market data.
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


class CareerGoalStatus(enum.Enum):
    """Career goal status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused" 
    COMPLETED = "completed"
    ARCHIVED = "archived"


class LearningPathStatus(enum.Enum):
    """Learning path status enumeration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OUTDATED = "outdated"


class Priority(enum.Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CareerGoal(Base):
    """User career goals and aspirations"""
    __tablename__ = "career_goals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Goal Details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_position = Column(String(100))
    target_company = Column(String(100))
    target_industry = Column(String(100))
    target_salary_min = Column(Integer)
    target_salary_max = Column(Integer)
    
    # Timeline
    target_date = Column(DateTime(timezone=True))
    estimated_duration_months = Column(Integer)
    
    # Status and Priority
    status = Column(Enum(CareerGoalStatus), default=CareerGoalStatus.ACTIVE)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    progress_percentage = Column(Integer, default=0)
    
    # AI-Generated Insights
    market_feasibility_score = Column(Float)  # 0.0-1.0
    skill_gap_analysis = Column(JSON)  # AI analysis of required vs current skills
    recommended_timeline = Column(JSON)  # AI-suggested milestones
    market_trends = Column(JSON)  # Relevant market data
    
    # Personalization
    motivation_factors = Column(JSON)  # What drives this goal
    obstacles = Column(JSON)  # Identified challenges
    success_metrics = Column(JSON)  # How success will be measured
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_reviewed = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="career_goals")
    learning_paths = relationship("LearningPath", back_populates="career_goal")


class LearningPath(Base):
    """Personalized learning paths for career goals"""
    __tablename__ = "learning_paths"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    career_goal_id = Column(String(36), ForeignKey("career_goals.id"))
    
    # Path Details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    estimated_duration_weeks = Column(Integer)
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    
    # Structure
    modules = Column(JSON)  # Ordered list of learning modules
    milestones = Column(JSON)  # Key checkpoints and assessments
    prerequisites = Column(JSON)  # Required prior knowledge/skills
    learning_objectives = Column(JSON)  # What the user will achieve
    
    # Progress Tracking
    status = Column(Enum(LearningPathStatus), default=LearningPathStatus.NOT_STARTED)
    progress_percentage = Column(Integer, default=0)
    current_module_index = Column(Integer, default=0)
    
    # AI Optimization
    personalization_factors = Column(JSON)  # User preferences and constraints
    adaptive_adjustments = Column(JSON)  # AI-made modifications based on progress
    success_predictions = Column(JSON)  # ML predictions about completion likelihood
    
    # Quality Metrics
    effectiveness_score = Column(Float)  # How well this path works for similar users
    user_satisfaction_score = Column(Float)  # User feedback
    completion_rate = Column(Float)  # Historical completion rate
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    career_goal = relationship("CareerGoal", back_populates="learning_paths")


class SkillGap(Base):
    """Identified skill gaps based on career goals and market analysis"""
    __tablename__ = "skill_gaps"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    career_goal_id = Column(String(36), ForeignKey("career_goals.id"))
    
    # Gap Details
    skill_name = Column(String(100), nullable=False)
    skill_category = Column(String(50))
    current_level = Column(Integer, default=0)  # 0-5 scale
    required_level = Column(Integer, nullable=False)  # 0-5 scale
    gap_severity = Column(String(20))  # low, medium, high, critical
    
    # Market Context
    market_demand_score = Column(Float)  # 0.0-1.0
    salary_impact = Column(Float)  # Estimated salary increase from acquiring skill
    job_posting_frequency = Column(Integer)  # How often this skill appears in jobs
    trending_score = Column(Float)  # How fast demand is growing
    
    # Learning Recommendations
    recommended_resources = Column(JSON)  # Courses, books, projects
    estimated_learning_time_hours = Column(Integer)
    learning_difficulty = Column(String(20))
    practice_opportunities = Column(JSON)  # Ways to apply the skill
    
    # Priority and Planning
    priority_score = Column(Float)  # AI-calculated priority (0.0-1.0)
    suggested_order = Column(Integer)  # Recommended learning sequence
    dependencies = Column(JSON)  # Other skills needed first
    
    # Status Tracking
    is_addressed = Column(Boolean, default=False)
    started_learning_at = Column(DateTime(timezone=True))
    target_completion_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobMarketData(Base):
    """Real-time job market intelligence"""
    __tablename__ = "job_market_data"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Job Details
    job_title = Column(String(200), nullable=False)
    company = Column(String(100))
    location = Column(String(100))
    remote_options = Column(String(50))  # remote, hybrid, onsite
    employment_type = Column(String(50))  # full-time, part-time, contract
    
    # Requirements
    required_skills = Column(JSON)  # List of required skills
    preferred_skills = Column(JSON)  # List of preferred skills
    experience_level = Column(String(50))
    education_requirements = Column(String(200))
    certifications = Column(JSON)
    
    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(10), default="USD")
    benefits = Column(JSON)
    equity_offered = Column(Boolean, default=False)
    
    # Source and Quality
    source_platform = Column(String(50))  # LinkedIn, Indeed, etc.
    source_url = Column(String(500))
    posting_date = Column(DateTime(timezone=True))
    application_deadline = Column(DateTime(timezone=True))
    data_quality_score = Column(Float)  # 0.0-1.0
    
    # Analysis
    skill_tags = Column(JSON)  # Normalized skill categories
    seniority_level = Column(String(20))
    industry_tags = Column(JSON)
    company_size = Column(String(20))
    growth_stage = Column(String(20))  # startup, growth, enterprise
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_verified = Column(DateTime(timezone=True))
