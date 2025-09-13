"""Career Coaching API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.services.career_pathing_service import CareerPathingService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()
career_service = CareerPathingService()


class CareerGoalRequest(BaseModel):
    """Request model for creating career roadmap"""
    career_goal: str = Field(..., description="Target career goal (e.g., 'Data Analyst')")
    current_background: str = Field(..., description="User's current background and experience")
    experience_level: str = Field("beginner", description="Experience level: beginner, intermediate, advanced")
    timeline_months: int = Field(12, ge=1, le=36, description="Desired timeline in months")


class SkillDevelopmentRequest(BaseModel):
    """Request model for skill development plan"""
    skill_name: str = Field(..., description="Skill to develop")
    current_level: str = Field("beginner", description="Current skill level")
    target_level: str = Field("intermediate", description="Target skill level")
    timeline_weeks: int = Field(8, ge=1, le=24, description="Timeline in weeks")


class BackgroundAnalysisRequest(BaseModel):
    """Request model for background analysis"""
    resume_text: Optional[str] = None
    skills_list: Optional[List[str]] = None
    experience_description: Optional[str] = None


@router.post("/roadmap")
async def generate_career_roadmap(
    request: CareerGoalRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized career roadmap
    
    **Example Usage:**
    ```json
    {
        "career_goal": "Data Analyst",
        "current_background": "I'm a recent graduate with a degree in Business Administration. I have basic Excel skills and took one statistics course.",
        "experience_level": "beginner",
        "timeline_months": 12
    }
    ```
    
    **Response:** Comprehensive roadmap with top 5 skills, learning phases, projects, and market insights.
    """
    try:
        roadmap = await career_service.generate_career_roadmap(
            career_goal=request.career_goal,
            current_background=request.current_background,
            experience_level=request.experience_level,
            timeline_months=request.timeline_months,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "roadmap": roadmap,
            "message": f"Personalized roadmap generated for {request.career_goal}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


@router.post("/skill-development")
async def create_skill_development_plan(
    request: SkillDevelopmentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create detailed skill development plan
    
    **Example Usage:**
    ```json
    {
        "skill_name": "Data Visualization", 
        "current_level": "beginner",
        "target_level": "intermediate",
        "timeline_weeks": 8
    }
    ```
    
    **Response:** Comprehensive plan with learning resources, practical assignments, and weekly schedule.
    """
    try:
        plan = await career_service.get_skill_development_plan(
            skill_name=request.skill_name,
            current_level=request.current_level,
            target_level=request.target_level,
            timeline_weeks=request.timeline_weeks
        )
        
        return {
            "success": True,
            "development_plan": plan,
            "message": f"Development plan created for {request.skill_name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill plan generation failed: {str(e)}")


@router.post("/analyze-background")
async def analyze_user_background(
    request: BackgroundAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze user background for personalized recommendations
    
    **Example Usage:**
    ```json
    {
        "resume_text": "Software Engineer with 2 years experience in Python and React...",
        "skills_list": ["Python", "JavaScript", "SQL", "Git"],
        "experience_description": "Built web applications and worked with databases..."
    }
    ```
    
    **Response:** Detailed analysis with skill assessment, career readiness, and recommendations.
    """
    try:
        analysis = await career_service.analyze_user_background(
            resume_text=request.resume_text,
            skills_list=request.skills_list,
            experience_description=request.experience_description
        )
        
        return {
            "success": True,
            "background_analysis": analysis,
            "message": "Background analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Background analysis failed: {str(e)}")


@router.get("/sample-goals")
async def get_sample_career_goals():
    """Get sample career goals for inspiration"""
    return {
        "popular_goals": [
            {
                "title": "Data Analyst",
                "description": "Analyze data to help businesses make informed decisions",
                "skills": ["SQL", "Python", "Data Visualization", "Statistics", "Excel"],
                "avg_timeline": "8-12 months",
                "market_demand": "high"
            },
            {
                "title": "Software Engineer",
                "description": "Build web and mobile applications",
                "skills": ["JavaScript", "Python", "React", "Databases", "Git"],
                "avg_timeline": "6-18 months",
                "market_demand": "very high"
            },
            {
                "title": "Product Manager",
                "description": "Guide product development from concept to launch",
                "skills": ["Product Strategy", "Analytics", "Communication", "User Research", "Agile"],
                "avg_timeline": "12-24 months", 
                "market_demand": "high"
            },
            {
                "title": "UX Designer",
                "description": "Design user-friendly digital experiences",
                "skills": ["Design Thinking", "Figma", "User Research", "Prototyping", "Usability Testing"],
                "avg_timeline": "6-12 months",
                "market_demand": "high"
            },
            {
                "title": "Digital Marketing Specialist",
                "description": "Manage online marketing campaigns and strategy",
                "skills": ["SEO", "Google Ads", "Content Marketing", "Analytics", "Social Media"],
                "avg_timeline": "4-8 months",
                "market_demand": "high"
            },
            {
                "title": "Cybersecurity Analyst",
                "description": "Protect organizations from cyber threats",
                "skills": ["Network Security", "Risk Assessment", "Incident Response", "Security Tools", "Compliance"],
                "avg_timeline": "12-18 months",
                "market_demand": "very high"
            }
        ]
    }


@router.get("/market-trends/{career_goal}")
async def get_market_trends(
    career_goal: str,
    current_user: User = Depends(get_current_user)
):
    """Get current market trends for specific career goal"""
    try:
        # This would typically fetch real-time data
        # For now, return structured sample data
        trends = {
            "career_goal": career_goal,
            "market_outlook": "positive",
            "job_growth_rate": "8-15% annually",
            "average_salary_range": "$65,000 - $120,000",
            "in_demand_skills": [
                "Core technical skills",
                "Communication abilities", 
                "Problem-solving",
                "Adaptability"
            ],
            "top_hiring_companies": [
                "Technology companies",
                "Financial services",
                "Healthcare organizations",
                "Consulting firms"
            ],
            "certification_recommendations": [
                "Industry-specific certifications",
                "Platform-specific credentials",
                "Continuous learning programs"
            ],
            "market_insights": f"The {career_goal} field shows strong growth with increasing demand for skilled professionals.",
            "last_updated": "2024-01-01T00:00:00Z"
        }
        
        return {
            "success": True,
            "market_trends": trends
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market trends analysis failed: {str(e)}")


@router.get("/user-goals")
async def get_user_career_goals(
    current_user: User = Depends(get_current_user)
):
    """Get user's saved career goals and roadmaps"""
    try:
        # This would typically fetch from database
        # For now, return sample user goals
        user_goals = {
            "active_goals": [
                {
                    "id": "goal_1",
                    "career_goal": "Data Analyst", 
                    "status": "in_progress",
                    "progress_percentage": 35,
                    "created_at": "2024-01-01T00:00:00Z",
                    "target_completion": "2024-12-01T00:00:00Z"
                }
            ],
            "completed_goals": [],
            "draft_goals": []
        }
        
        return {
            "success": True,
            "user_goals": user_goals
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user goals: {str(e)}")
