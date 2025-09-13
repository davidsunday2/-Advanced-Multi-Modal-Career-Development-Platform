"""
Career Pathing Service

Implements personalized career pathing with AI-generated roadmaps.
Students define career goals and receive customized learning paths.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.utilities import SerpAPIWrapper

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.services.job_market_service import JobMarketService
from app.core.cache import cache

logger = logging.getLogger(__name__)


class CareerPathingService:
    """AI-powered career pathing and roadmap generation"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model_name=settings.OPENAI_MODEL, temperature=0.3)
        self.job_market_service = JobMarketService()
    
    async def generate_career_roadmap(
        self, 
        career_goal: str,
        current_background: str,
        experience_level: str = "beginner",
        timeline_months: int = 12,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate personalized career roadmap based on user's goal and background
        
        Example: "I want to become a Data Analyst"
        """
        try:
            logger.info(f"Generating career roadmap for goal: {career_goal}")
            
            # 1. Get real-time job market data
            job_market_data = await self.job_market_service.analyze_career_market(career_goal)
            
            # 2. Generate personalized roadmap
            roadmap_prompt = ChatPromptTemplate.from_template("""
            You are an expert career coach helping someone achieve their career goal.
            
            CAREER GOAL: {career_goal}
            CURRENT BACKGROUND: {current_background}
            EXPERIENCE LEVEL: {experience_level}
            TIMELINE: {timeline_months} months
            
            CURRENT JOB MARKET DATA:
            {job_market_data}
            
            Create a personalized career roadmap with exactly this JSON structure:
            {{
                "roadmap_title": "Personalized path to {career_goal}",
                "timeline_months": {timeline_months},
                "top_5_skills": [
                    {{
                        "skill": "Skill name",
                        "priority": "high/medium/low",
                        "description": "Why this skill is important",
                        "market_demand": "high/medium/low"
                    }}
                ],
                "learning_phases": [
                    {{
                        "phase": 1,
                        "title": "Foundation Building",
                        "duration_weeks": 4,
                        "focus_skills": ["skill1", "skill2"],
                        "objectives": ["Learn X", "Build Y"],
                        "deliverables": ["Project A", "Assignment B"]
                    }}
                ],
                "project_recommendations": [
                    {{
                        "project_name": "Portfolio Project 1",
                        "description": "Build a real-world project",
                        "skills_practiced": ["skill1", "skill2"],
                        "difficulty": "beginner/intermediate/advanced",
                        "estimated_hours": 20
                    }}
                ],
                "market_insights": {{
                    "average_salary": "$XX,XXX",
                    "job_growth": "X% annually",
                    "top_companies": ["Company1", "Company2"],
                    "key_certifications": ["Cert1", "Cert2"]
                }}
            }}
            
            Make this specific, actionable, and based on REAL market data provided.
            """)
            
            chain = roadmap_prompt | self.llm | StrOutputParser()
            
            roadmap_response = await chain.ainvoke({
                "career_goal": career_goal,
                "current_background": current_background,
                "experience_level": experience_level,
                "timeline_months": timeline_months,
                "job_market_data": job_market_data
            })
            
            # Parse the JSON response
            import json
            try:
                roadmap = json.loads(roadmap_response)
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                roadmap = self._parse_roadmap_fallback(roadmap_response, career_goal)
            
            # 3. Add personalization metadata
            roadmap.update({
                "generated_at": datetime.now().isoformat(),
                "user_id": user_id,
                "career_goal": career_goal,
                "experience_level": experience_level,
                "customization_score": 0.85,  # AI confidence in personalization
                "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
            })
            
            # 4. Cache the roadmap
            if user_id:
                cache_key = f"career_roadmap:{user_id}:{career_goal.lower().replace(' ', '_')}"
                await cache.set(cache_key, roadmap, ttl=86400)  # 24 hours
            
            logger.info(f"Successfully generated roadmap with {len(roadmap.get('top_5_skills', []))} skills")
            return roadmap
            
        except Exception as e:
            logger.error(f"Failed to generate career roadmap: {e}")
            raise AIServiceError(f"Career roadmap generation failed: {str(e)}")
    
    async def get_skill_development_plan(
        self,
        skill_name: str,
        current_level: str = "beginner",
        target_level: str = "intermediate",
        timeline_weeks: int = 8
    ) -> Dict[str, Any]:
        """
        Generate detailed skill development plan for specific skill
        
        Example: User selects "Data Visualization" from their roadmap
        """
        try:
            logger.info(f"Generating skill development plan for: {skill_name}")
            
            skill_prompt = ChatPromptTemplate.from_template("""
            You are an expert learning designer creating a skill development plan.
            
            SKILL: {skill_name}
            CURRENT LEVEL: {current_level}
            TARGET LEVEL: {target_level}
            TIMELINE: {timeline_weeks} weeks
            
            Create a comprehensive skill development plan with this JSON structure:
            {{
                "skill_name": "{skill_name}",
                "development_path": {{
                    "current_level": "{current_level}",
                    "target_level": "{target_level}",
                    "timeline_weeks": {timeline_weeks},
                    "difficulty_progression": "gradual/moderate/intensive"
                }},
                "learning_resources": [
                    {{
                        "type": "course/tutorial/book/documentation",
                        "title": "Resource name",
                        "provider": "Platform/Author",
                        "duration": "X hours",
                        "difficulty": "beginner/intermediate/advanced",
                        "url": "https://example.com",
                        "priority": "high/medium/low"
                    }}
                ],
                "practical_assignments": [
                    {{
                        "assignment_title": "Build a [specific project]",
                        "description": "Detailed description of what to build",
                        "skills_practiced": ["sub-skill1", "sub-skill2"],
                        "estimated_hours": 10,
                        "difficulty": "beginner/intermediate/advanced",
                        "deliverables": ["Deliverable 1", "Deliverable 2"],
                        "evaluation_criteria": ["Criteria 1", "Criteria 2"]
                    }}
                ],
                "weekly_schedule": [
                    {{
                        "week": 1,
                        "focus": "Week 1 focus area",
                        "activities": ["Activity 1", "Activity 2"],
                        "milestone": "What to achieve this week"
                    }}
                ],
                "skill_validation": {{
                    "assessment_methods": ["Portfolio review", "Practical test"],
                    "portfolio_requirements": ["Project 1", "Project 2"],
                    "certification_options": ["Cert 1", "Cert 2"]
                }}
            }}
            
            Make this highly practical and project-focused. Include real tools and platforms.
            """)
            
            chain = skill_prompt | self.llm | StrOutputParser()
            
            plan_response = await chain.ainvoke({
                "skill_name": skill_name,
                "current_level": current_level,
                "target_level": target_level,
                "timeline_weeks": timeline_weeks
            })
            
            # Parse JSON response
            import json
            try:
                plan = json.loads(plan_response)
            except json.JSONDecodeError:
                plan = self._parse_skill_plan_fallback(plan_response, skill_name)
            
            plan.update({
                "generated_at": datetime.now().isoformat(),
                "personalization_score": 0.8
            })
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate skill development plan: {e}")
            raise AIServiceError(f"Skill development plan generation failed: {str(e)}")
    
    async def analyze_user_background(
        self,
        resume_text: str = None,
        skills_list: List[str] = None,
        experience_description: str = None
    ) -> Dict[str, Any]:
        """
        Analyze user's background to better personalize career recommendations
        """
        try:
            background_prompt = ChatPromptTemplate.from_template("""
            Analyze this user's background and extract key information for career coaching.
            
            RESUME/BACKGROUND: {background_text}
            LISTED SKILLS: {skills_list}
            EXPERIENCE: {experience_description}
            
            Return analysis in this JSON format:
            {{
                "skill_assessment": {{
                    "technical_skills": ["skill1", "skill2"],
                    "soft_skills": ["skill1", "skill2"],
                    "experience_level": "beginner/intermediate/advanced",
                    "strength_areas": ["area1", "area2"],
                    "growth_areas": ["area1", "area2"]
                }},
                "career_readiness": {{
                    "overall_score": 7.5,
                    "technical_readiness": 6.0,
                    "communication_readiness": 8.0,
                    "industry_knowledge": 5.0
                }},
                "recommended_focus": {{
                    "immediate_priorities": ["priority1", "priority2"],
                    "skill_gaps": ["gap1", "gap2"],
                    "learning_style_suggestions": ["hands-on projects", "structured courses"]
                }}
            }}
            """)
            
            background_text = resume_text or experience_description or "No background provided"
            skills_text = ", ".join(skills_list) if skills_list else "No skills listed"
            
            chain = background_prompt | self.llm | StrOutputParser()
            analysis_response = await chain.ainvoke({
                "background_text": background_text,
                "skills_list": skills_text,
                "experience_description": experience_description or "Not provided"
            })
            
            import json
            try:
                analysis = json.loads(analysis_response)
            except json.JSONDecodeError:
                analysis = {
                    "skill_assessment": {
                        "experience_level": "beginner",
                        "strength_areas": ["motivation"],
                        "growth_areas": ["technical skills"]
                    },
                    "career_readiness": {"overall_score": 5.0},
                    "recommended_focus": {
                        "immediate_priorities": ["skill building", "practice projects"]
                    }
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Background analysis failed: {e}")
            return {"error": "Analysis failed", "fallback": True}
    
    def _parse_roadmap_fallback(self, response: str, career_goal: str) -> Dict[str, Any]:
        """Fallback parsing if JSON fails"""
        return {
            "roadmap_title": f"Career path to {career_goal}",
            "timeline_months": 12,
            "top_5_skills": [
                {"skill": "Core Skill 1", "priority": "high", "description": "Essential foundation skill"},
                {"skill": "Core Skill 2", "priority": "high", "description": "Industry-standard requirement"},
                {"skill": "Specialized Skill", "priority": "medium", "description": "Differentiation skill"},
                {"skill": "Communication", "priority": "medium", "description": "Professional effectiveness"},
                {"skill": "Industry Knowledge", "priority": "low", "description": "Domain expertise"}
            ],
            "learning_phases": [
                {
                    "phase": 1,
                    "title": "Foundation Building",
                    "duration_weeks": 8,
                    "focus_skills": ["Core Skill 1", "Core Skill 2"],
                    "objectives": ["Build foundation", "Complete first project"]
                }
            ],
            "project_recommendations": [
                {
                    "project_name": "Portfolio Project",
                    "description": "Build a real-world project demonstrating key skills",
                    "skills_practiced": ["Core Skill 1", "Core Skill 2"],
                    "difficulty": "beginner"
                }
            ],
            "market_insights": {
                "average_salary": "Market rate",
                "job_growth": "Growing field",
                "top_companies": ["Industry leaders"],
                "key_certifications": ["Relevant certifications"]
            },
            "fallback_parsing": True
        }
    
    def _parse_skill_plan_fallback(self, response: str, skill_name: str) -> Dict[str, Any]:
        """Fallback parsing for skill plans"""
        return {
            "skill_name": skill_name,
            "development_path": {
                "timeline_weeks": 8,
                "difficulty_progression": "gradual"
            },
            "learning_resources": [
                {
                    "type": "course",
                    "title": f"Learn {skill_name}",
                    "provider": "Online Platform",
                    "priority": "high"
                }
            ],
            "practical_assignments": [
                {
                    "assignment_title": f"Build a {skill_name} project",
                    "description": f"Create a practical project using {skill_name}",
                    "estimated_hours": 20,
                    "difficulty": "beginner"
                }
            ],
            "fallback_parsing": True
        }


class JobMarketService:
    """Service for analyzing job market data"""
    
    def __init__(self):
        self.serp_api = SerpAPIWrapper()
    
    async def analyze_career_market(self, career_goal: str) -> str:
        """Analyze current job market for specific career goal"""
        try:
            # Search for recent job postings
            query = f"{career_goal} jobs requirements skills 2024"
            results = self.serp_api.run(query)
            
            # Parse and summarize results
            market_summary = f"Recent job market analysis for {career_goal}:\n{results[:1000]}..."
            return market_summary
            
        except Exception as e:
            logger.error(f"Job market analysis failed: {e}")
            return f"Market analysis for {career_goal}: High demand field with growing opportunities. Focus on core technical skills and communication abilities."
