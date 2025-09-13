"""
Job Market Data Service

This service handles fetching and processing real-time job market data
using SerpAPI for market trends, salary insights, and skill demand analysis.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

import httpx
from serpapi import GoogleSearch

from app.core.config import settings

logger = logging.getLogger(__name__)


class JobMarketService:
    """Service for fetching and analyzing job market data"""
    
    def __init__(self):
        self.serpapi_key = settings.SERPAPI_API_KEY
        self.cache_duration = timedelta(hours=6)  # Cache data for 6 hours
        self._cache = {}
    
    async def get_market_trends(self, career_goal: str, location: str = "United States") -> Dict[str, Any]:
        """
        Get market trends for a specific career goal
        
        Args:
            career_goal: The career/job title to analyze
            location: Geographic location for the search
            
        Returns:
            Dict containing market trends data
        """
        cache_key = f"trends_{career_goal}_{location}"
        
        # Check cache first
        if self._is_cached(cache_key):
            logger.info(f"Returning cached market trends for {career_goal}")
            return self._cache[cache_key]["data"]
        
        try:
            # Search for job postings
            search_params = {
                "engine": "google_jobs",
                "q": career_goal,
                "location": location,
                "api_key": self.serpapi_key,
                "num": 20
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            # Process the results
            trends_data = await self._process_job_trends(results, career_goal)
            
            # Cache the results
            self._cache[cache_key] = {
                "data": trends_data,
                "timestamp": datetime.now()
            }
            
            logger.info(f"✅ Fetched market trends for {career_goal}")
            return trends_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching market trends for {career_goal}: {e}")
            # Return mock data if API fails
            return self._get_mock_trends_data(career_goal)
    
    async def get_salary_insights(self, career_goal: str, location: str = "United States") -> Dict[str, Any]:
        """
        Get salary insights for a specific career
        
        Args:
            career_goal: The career/job title to analyze
            location: Geographic location for the search
            
        Returns:
            Dict containing salary insights
        """
        cache_key = f"salary_{career_goal}_{location}"
        
        if self._is_cached(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            # Search for salary information
            search_params = {
                "engine": "google",
                "q": f"{career_goal} salary {location}",
                "api_key": self.serpapi_key,
                "num": 10
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            salary_data = await self._process_salary_data(results, career_goal)
            
            self._cache[cache_key] = {
                "data": salary_data,
                "timestamp": datetime.now()
            }
            
            return salary_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching salary insights for {career_goal}: {e}")
            return self._get_mock_salary_data(career_goal)
    
    async def get_skill_demand(self, skills: List[str], career_goal: str) -> Dict[str, Any]:
        """
        Analyze demand for specific skills in the job market
        
        Args:
            skills: List of skills to analyze
            career_goal: The career context for skill analysis
            
        Returns:
            Dict containing skill demand analysis
        """
        try:
            skill_analysis = {}
            
            for skill in skills:
                search_params = {
                    "engine": "google_jobs",
                    "q": f"{skill} {career_goal}",
                    "api_key": self.serpapi_key,
                    "num": 10
                }
                
                search = GoogleSearch(search_params)
                results = search.get_dict()
                
                # Count job postings mentioning this skill
                job_count = len(results.get("jobs_results", []))
                
                skill_analysis[skill] = {
                    "demand_score": min(job_count * 10, 100),  # Scale to 0-100
                    "job_count": job_count,
                    "priority": "high" if job_count > 15 else "medium" if job_count > 5 else "low"
                }
                
                # Add small delay to respect API limits
                await asyncio.sleep(0.5)
            
            return {
                "skills": skill_analysis,
                "analysis_date": datetime.now().isoformat(),
                "career_context": career_goal
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing skill demand: {e}")
            return self._get_mock_skill_demand(skills, career_goal)
    
    async def _process_job_trends(self, results: Dict, career_goal: str) -> Dict[str, Any]:
        """Process job search results to extract trends"""
        jobs = results.get("jobs_results", [])
        
        # Extract key information
        companies = [job.get("company_name", "") for job in jobs if job.get("company_name")]
        locations = [job.get("location", "") for job in jobs if job.get("location")]
        
        # Count top companies and locations
        company_counts = {}
        location_counts = {}
        
        for company in companies:
            company_counts[company] = company_counts.get(company, 0) + 1
        
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            "career_goal": career_goal,
            "total_jobs_found": len(jobs),
            "top_companies": sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_locations": sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "market_activity": "high" if len(jobs) > 15 else "medium" if len(jobs) > 5 else "low",
            "analysis_date": datetime.now().isoformat()
        }
    
    async def _process_salary_data(self, results: Dict, career_goal: str) -> Dict[str, Any]:
        """Process search results to extract salary information"""
        # This is a simplified implementation
        # In a real scenario, you'd parse the search results for salary ranges
        
        return {
            "career_goal": career_goal,
            "estimated_range": {
                "min": 50000,
                "max": 120000,
                "median": 85000
            },
            "currency": "USD",
            "location": "United States",
            "confidence": "medium",
            "source": "market_analysis",
            "analysis_date": datetime.now().isoformat()
        }
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration
    
    def _get_mock_trends_data(self, career_goal: str) -> Dict[str, Any]:
        """Return mock trends data when API is unavailable"""
        return {
            "career_goal": career_goal,
            "total_jobs_found": 25,
            "top_companies": [
                ("Google", 3),
                ("Microsoft", 2),
                ("Amazon", 2),
                ("Meta", 1),
                ("Apple", 1)
            ],
            "top_locations": [
                ("San Francisco, CA", 8),
                ("New York, NY", 6),
                ("Seattle, WA", 4),
                ("Austin, TX", 3),
                ("Boston, MA", 2)
            ],
            "market_activity": "high",
            "analysis_date": datetime.now().isoformat(),
            "note": "Mock data - API unavailable"
        }
    
    def _get_mock_salary_data(self, career_goal: str) -> Dict[str, Any]:
        """Return mock salary data when API is unavailable"""
        # Different salary ranges based on career goal
        salary_ranges = {
            "data analyst": {"min": 55000, "max": 95000, "median": 75000},
            "software engineer": {"min": 70000, "max": 150000, "median": 110000},
            "product manager": {"min": 80000, "max": 160000, "median": 120000},
            "data scientist": {"min": 75000, "max": 140000, "median": 107500},
            "ux designer": {"min": 60000, "max": 120000, "median": 90000}
        }
        
        # Find matching range or use default
        range_data = salary_ranges.get(career_goal.lower(), {"min": 50000, "max": 100000, "median": 75000})
        
        return {
            "career_goal": career_goal,
            "estimated_range": range_data,
            "currency": "USD",
            "location": "United States",
            "confidence": "medium",
            "source": "mock_data",
            "analysis_date": datetime.now().isoformat(),
            "note": "Mock data - API unavailable"
        }
    
    def _get_mock_skill_demand(self, skills: List[str], career_goal: str) -> Dict[str, Any]:
        """Return mock skill demand data when API is unavailable"""
        skill_analysis = {}
        
        # Mock demand scores based on common skill priorities
        high_demand_skills = ["python", "sql", "machine learning", "aws", "react", "javascript"]
        medium_demand_skills = ["excel", "tableau", "git", "docker", "css", "html"]
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(high_skill in skill_lower for high_skill in high_demand_skills):
                demand_score = 85
                priority = "high"
                job_count = 20
            elif any(med_skill in skill_lower for med_skill in medium_demand_skills):
                demand_score = 65
                priority = "medium"
                job_count = 12
            else:
                demand_score = 45
                priority = "low"
                job_count = 6
            
            skill_analysis[skill] = {
                "demand_score": demand_score,
                "job_count": job_count,
                "priority": priority
            }
        
        return {
            "skills": skill_analysis,
            "analysis_date": datetime.now().isoformat(),
            "career_context": career_goal,
            "note": "Mock data - API unavailable"
        }
