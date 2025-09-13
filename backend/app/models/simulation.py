"""
Simulation Models

Defines simulation-related database models for professional scenario practice.
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


class SimulationType(enum.Enum):
    """Types of professional simulations"""
    TECHNICAL_INTERVIEW = "technical_interview"
    BEHAVIORAL_INTERVIEW = "behavioral_interview"
    STAKEHOLDER_MEETING = "stakeholder_meeting"
    PRESENTATION = "presentation"
    NEGOTIATION = "negotiation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    TEAM_LEADERSHIP = "team_leadership"
    CLIENT_CONSULTATION = "client_consultation"
    PERFORMANCE_REVIEW = "performance_review"
    SALES_PITCH = "sales_pitch"


class SimulationDifficulty(enum.Enum):
    """Simulation difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SessionStatus(enum.Enum):
    """Simulation session status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class InteractionMode(enum.Enum):
    """How the user interacts with the simulation"""
    TEXT_ONLY = "text_only"
    VOICE_ONLY = "voice_only"
    MIXED = "mixed"


class Simulation(Base):
    """Simulation templates and configurations"""
    __tablename__ = "simulations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    simulation_type = Column(Enum(SimulationType), nullable=False)
    difficulty = Column(Enum(SimulationDifficulty), default=SimulationDifficulty.INTERMEDIATE)
    
    # Configuration
    estimated_duration_minutes = Column(Integer, default=30)
    max_duration_minutes = Column(Integer, default=60)
    supported_interaction_modes = Column(JSON)  # List of supported modes
    
    # AI Configuration
    ai_persona_config = Column(JSON)  # AI character configuration
    scenario_prompts = Column(JSON)  # Scenario setup and context
    evaluation_criteria = Column(JSON)  # How performance is measured
    adaptive_difficulty = Column(Boolean, default=True)
    
    # Learning Objectives
    skills_practiced = Column(JSON)  # Skills this simulation helps develop
    learning_outcomes = Column(JSON)  # Expected learning outcomes
    prerequisite_skills = Column(JSON)  # Required baseline skills
    
    # Content Structure
    phases = Column(JSON)  # Simulation phases/stages
    decision_points = Column(JSON)  # Key decision moments
    success_scenarios = Column(JSON)  # Different ways to succeed
    failure_scenarios = Column(JSON)  # Common failure modes
    
    # Metadata
    industry_focus = Column(String(100))
    role_focus = Column(String(100))
    popularity_score = Column(Float, default=0.0)
    effectiveness_rating = Column(Float, default=0.0)
    
    # Management
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_by = Column(String(100))  # Creator/author
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sessions = relationship("SimulationSession", back_populates="simulation")


class SimulationSession(Base):
    """Individual simulation session instances"""
    __tablename__ = "simulation_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    simulation_id = Column(String(36), ForeignKey("simulations.id"))
    
    # Session Configuration
    interaction_mode = Column(Enum(InteractionMode), default=InteractionMode.MIXED)
    difficulty_override = Column(Enum(SimulationDifficulty))  # Override template difficulty
    custom_parameters = Column(JSON)  # User-specific customizations
    
    # Session State
    status = Column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    current_phase = Column(String(50))
    session_data = Column(JSON)  # Dynamic session state
    
    # Performance Data
    performance_score = Column(Float)  # Overall performance (0.0-1.0)
    skill_scores = Column(JSON)  # Breakdown by skill
    decision_quality = Column(Float)  # Quality of decisions made
    communication_score = Column(Float)  # Communication effectiveness
    
    # Interaction Metrics
    total_interactions = Column(Integer, default=0)
    response_times = Column(JSON)  # Response time analytics
    transcript = Column(JSON)  # Full conversation transcript
    audio_recordings = Column(JSON)  # Audio file references
    
    # Time Tracking
    scheduled_start = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    total_duration_seconds = Column(Integer)
    pause_duration_seconds = Column(Integer, default=0)
    
    # AI Behavior
    ai_persona_used = Column(JSON)  # AI character that was used
    ai_adaptations = Column(JSON)  # How AI adapted during session
    ai_intervention_points = Column(JSON)  # When AI provided help
    
    # Quality Control
    completion_percentage = Column(Float, default=0.0)
    user_satisfaction_rating = Column(Integer)  # 1-5 scale
    technical_issues = Column(JSON)  # Any technical problems
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="simulation_sessions")
    simulation = relationship("Simulation", back_populates="sessions")
    feedback = relationship("SimulationFeedback", back_populates="session", uselist=False)


class SimulationFeedback(Base):
    """AI-generated feedback for simulation sessions"""
    __tablename__ = "simulation_feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("simulation_sessions.id"), unique=True)
    
    # Overall Assessment
    overall_summary = Column(Text)
    strengths_identified = Column(JSON)  # What the user did well
    improvement_areas = Column(JSON)  # What needs work
    
    # Detailed Analysis
    communication_feedback = Column(JSON)  # Communication-specific feedback
    technical_feedback = Column(JSON)  # Technical skill feedback
    behavioral_feedback = Column(JSON)  # Soft skill feedback
    decision_making_feedback = Column(JSON)  # Decision quality feedback
    
    # Specific Recommendations
    immediate_actions = Column(JSON)  # Things to practice right away
    long_term_development = Column(JSON)  # Longer-term skill building
    resource_recommendations = Column(JSON)  # Suggested learning resources
    practice_suggestions = Column(JSON)  # Ways to practice further
    
    # Comparative Analysis
    peer_comparison = Column(JSON)  # How user compares to similar users
    industry_benchmarks = Column(JSON)  # Industry standard comparisons
    improvement_trajectory = Column(JSON)  # Predicted improvement path
    
    # AI Analysis Metadata
    analysis_confidence = Column(Float)  # AI confidence in assessment (0.0-1.0)
    model_version = Column(String(50))  # AI model version used
    analysis_duration_seconds = Column(Integer)
    
    # User Interaction
    user_rating = Column(Integer)  # User rating of feedback quality (1-5)
    user_notes = Column(Text)  # User's own notes/reflections
    follow_up_scheduled = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("SimulationSession", back_populates="feedback")
