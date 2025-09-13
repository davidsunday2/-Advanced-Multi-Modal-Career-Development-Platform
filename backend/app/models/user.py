"""
User Models

Defines user-related database models including authentication, profiles, and skills.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, JSON, Enum
# from sqlalchemy.dialects.postgresql import UUID  # Not compatible with SQLite
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    PROFESSIONAL = "professional"
    EDUCATOR = "educator"
    ADMIN = "admin"


class ExperienceLevel(enum.Enum):
    """Experience level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(enum.Enum):
    """Learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory" 
    KINESTHETIC = "kinesthetic"
    READING = "reading"


class User(Base):
    """User authentication and basic information"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    skills = relationship("UserSkill", back_populates="user")
    career_goals = relationship("CareerGoal", back_populates="user")
    simulation_sessions = relationship("SimulationSession", back_populates="user")
    progress_records = relationship("UserProgress", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")


class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    
    # Personal Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    bio = Column(Text)
    location = Column(String(100))
    timezone = Column(String(50), default="UTC")
    
    # Professional Information
    current_position = Column(String(100))
    company = Column(String(100))
    industry = Column(String(100))
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.BEGINNER)
    years_of_experience = Column(Integer, default=0)
    
    # Education
    education_level = Column(String(100))
    field_of_study = Column(String(100))
    institution = Column(String(200))
    graduation_year = Column(Integer)
    
    # Learning Preferences
    learning_styles = Column(JSON)  # List of preferred learning styles
    preferred_time_slots = Column(JSON)  # Preferred times for learning/simulations
    weekly_learning_hours = Column(Integer, default=5)
    
    # Social Links
    linkedin_url = Column(String(255))
    github_url = Column(String(255))
    portfolio_url = Column(String(255))
    
    # Profile Completeness
    profile_completion_score = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")


class UserSkill(Base):
    """User skills and proficiency levels"""
    __tablename__ = "user_skills"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Skill Information
    skill_name = Column(String(100), nullable=False)
    category = Column(String(50))  # technical, soft, domain-specific
    proficiency_level = Column(Integer, default=1)  # 1-5 scale
    confidence_score = Column(Integer, default=50)  # 0-100
    
    # Skill Evidence
    source = Column(String(100))  # self-reported, assessment, certification
    evidence_url = Column(String(255))  # Link to portfolio, certificate, etc.
    verification_status = Column(String(20), default="unverified")
    
    # Progress Tracking
    initial_level = Column(Integer, default=1)
    target_level = Column(Integer, default=5)
    improvement_rate = Column(Integer, default=0)  # Points per week
    
    # Market Data
    market_demand_score = Column(Integer, default=50)  # 0-100 based on job market
    salary_impact_score = Column(Integer, default=50)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_practiced = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="skills")
