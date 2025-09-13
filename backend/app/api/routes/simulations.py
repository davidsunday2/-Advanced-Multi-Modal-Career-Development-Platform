"""Simulation API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

from app.services.simulation_engine import SimulationEngine, SimulationScenario
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()
simulation_engine = SimulationEngine()


class SimulationStartRequest(BaseModel):
    """Request model for starting simulation"""
    scenario: str = Field(..., description="Simulation scenario type")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for simulation")


class SimulationResponseRequest(BaseModel):
    """Request model for user response in simulation"""
    message: str = Field(..., description="User's response message")
    message_type: str = Field("text", description="Type of message: text or voice")


@router.get("/available")
async def get_available_simulations():
    """
    Get available simulation scenarios
    
    **Response:** List of all available professional simulation scenarios with descriptions.
    """
    return {
        "scenarios": [
            {
                "id": "stakeholder_meeting",
                "title": "Stakeholder Meeting",
                "description": "Present your findings to a non-technical manager who needs to understand business impact",
                "difficulty": "intermediate",
                "estimated_duration": "15-20 minutes",
                "skills_practiced": [
                    "Business communication",
                    "Data translation", 
                    "Stakeholder management",
                    "Presentation skills"
                ],
                "ai_persona": "Non-technical Product Manager",
                "learning_objectives": [
                    "Translate technical concepts to business language",
                    "Handle non-technical questions effectively",
                    "Present data in an understandable way"
                ],
                "example_scenario": "You've completed your data analysis. Present findings to Sarah Johnson (Product Manager) who needs to understand the business impact."
            },
            {
                "id": "technical_interview",
                "title": "Technical Interview",
                "description": "Practice technical questions and demonstrate problem-solving approach",
                "difficulty": "advanced",
                "estimated_duration": "20-30 minutes",
                "skills_practiced": [
                    "Technical communication",
                    "Problem-solving methodology",
                    "System design thinking",
                    "Coding explanation"
                ],
                "ai_persona": "Senior Software Engineer",
                "learning_objectives": [
                    "Explain technical concepts clearly",
                    "Demonstrate problem-solving methodology",
                    "Handle technical pressure effectively"
                ],
                "example_scenario": "Practice technical screening with Alex Chen (Senior Engineer). Explain concepts clearly and show your thought process."
            },
            {
                "id": "behavioral_interview", 
                "title": "Behavioral Interview",
                "description": "Answer behavioral questions using specific examples from experience",
                "difficulty": "beginner",
                "estimated_duration": "15-25 minutes",
                "skills_practiced": [
                    "STAR method",
                    "Self-reflection",
                    "Professional storytelling",
                    "Soft skills demonstration"
                ],
                "ai_persona": "HR Business Partner",
                "learning_objectives": [
                    "Use STAR method effectively",
                    "Provide specific, relevant examples",
                    "Demonstrate soft skills and growth"
                ],
                "example_scenario": "Behavioral interview with Jordan Martinez (HR). Use specific examples to demonstrate your experience and growth."
            }
        ]
    }


@router.post("/start")
async def start_simulation(
    request: SimulationStartRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Start a new simulation session
    
    **Example Usage:**
    ```json
    {
        "scenario": "stakeholder_meeting",
        "context": {
            "analysis_topic": "Website conversion rates",
            "business_context": "Quarterly review meeting",
            "urgency": "medium"
        }
    }
    ```
    
    **Response:** Session details with opening AI message and instructions.
    """
    try:
        # Validate scenario
        try:
            scenario_enum = SimulationScenario(request.scenario)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid scenario: {request.scenario}")
        
        # Start simulation
        session_data = await simulation_engine.start_simulation(
            scenario=scenario_enum,
            user_id=current_user.id,
            context=request.context
        )
        
        return {
            "success": True,
            "session": session_data,
            "message": f"Started {request.scenario} simulation successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start simulation: {str(e)}")


@router.post("/session/{session_id}/respond")
async def respond_to_simulation(
    session_id: str,
    request: SimulationResponseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send user response to active simulation
    
    **Example Usage:**
    ```json
    {
        "message": "Based on my analysis, I found that our conversion rate dropped 15% due to three main factors: page load time increased by 200ms, we had a checkout flow bug, and mobile optimization issues...",
        "message_type": "text"
    }
    ```
    
    **Response:** AI response with feedback and performance metrics.
    """
    try:
        response_data = await simulation_engine.process_user_response(
            session_id=session_id,
            user_message=request.message,
            message_type=request.message_type
        )
        
        return {
            "success": True,
            "ai_response": response_data["ai_response"],
            "current_phase": response_data["current_phase"],
            "performance_feedback": response_data.get("performance_feedback"),
            "phase_transition": response_data.get("phase_transition"),
            "session_metrics": response_data["session_metrics"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")


@router.post("/session/{session_id}/end")
async def end_simulation(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    End simulation session and get comprehensive feedback
    
    **Response:** Final performance scores, detailed feedback, and improvement suggestions.
    """
    try:
        final_data = await simulation_engine.end_simulation(session_id)
        
        return {
            "success": True,
            "final_feedback": final_data["final_feedback"],
            "final_scores": final_data["final_scores"],
            "conversation_summary": final_data["conversation_summary"],
            "improvement_suggestions": final_data["improvement_suggestions"],
            "next_steps": final_data["next_steps"],
            "message": "Simulation completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end simulation: {str(e)}")


@router.get("/session/{session_id}/status")
async def get_simulation_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current status of simulation session"""
    try:
        # This would fetch session state from cache/database
        session_state = await simulation_engine._get_session_state(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "scenario": session_state["scenario"],
            "current_phase": session_state["current_phase"],
            "conversation_length": len(session_state["conversation_history"]),
            "performance_metrics": session_state["performance_metrics"],
            "started_at": session_state["started_at"],
            "last_activity": session_state["last_activity"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")


@router.get("/user-sessions")
async def get_user_simulation_sessions(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    status: Optional[str] = None
):
    """Get user's simulation session history"""
    try:
        # This would typically fetch from database
        # For now, return sample session history
        sessions = [
            {
                "session_id": "session_123",
                "scenario": "stakeholder_meeting",
                "status": "completed",
                "final_score": 8.5,
                "duration_minutes": 18,
                "completed_at": "2024-01-01T10:30:00Z",
                "key_feedback": "Great technical explanation, work on business translation"
            },
            {
                "session_id": "session_124", 
                "scenario": "technical_interview",
                "status": "completed",
                "final_score": 7.2,
                "duration_minutes": 25,
                "completed_at": "2024-01-02T14:15:00Z",
                "key_feedback": "Strong problem-solving approach, clarify communication"
            }
        ]
        
        return {
            "success": True,
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user sessions: {str(e)}")


@router.get("/sample-scenarios")
async def get_sample_simulation_scenarios():
    """Get detailed sample scenarios for each simulation type"""
    return {
        "sample_scenarios": {
            "stakeholder_meeting": {
                "setup": "You've just completed a comprehensive analysis of website conversion rates. The data shows a 15% decline over the past quarter. You need to present your findings to Sarah Johnson, the Product Manager, who will decide on next steps and budget allocation.",
                "sample_conversation": [
                    {
                        "ai": "Hi! I'm Sarah, the Product Manager. I understand you've completed the conversion rate analysis. I'm really concerned about this 15% drop - walk me through what you found.",
                        "user_example": "Hi Sarah. Yes, I completed the analysis and identified three main factors causing the decline. The most significant is page load time - it increased by 200ms which correlates directly with the conversion drop.",
                        "ai_followup": "200ms doesn't sound like much - how does that actually translate to lost revenue? And what's causing this slowdown?"
                    }
                ],
                "coaching_tips": [
                    "Start with the business impact (revenue/conversion loss)",
                    "Use simple analogies for technical concepts",
                    "Have specific numbers and recommendations ready",
                    "Anticipate questions about cost and timeline"
                ]
            },
            "technical_interview": {
                "setup": "You're interviewing for a Software Engineer position. Alex Chen, a Senior Engineer, will assess your technical knowledge and problem-solving approach. The interview focuses on algorithms, system design, and coding best practices.",
                "sample_conversation": [
                    {
                        "ai": "Hi, I'm Alex. Let's start with a coding question. Can you explain the difference between supervised and unsupervised learning, and give me a practical example of each?",
                        "user_example": "Sure! Supervised learning uses labeled training data to predict outcomes - like email spam detection where we train on emails already marked as spam or not spam. Unsupervised learning finds patterns in data without labels - like customer segmentation where we group customers by behavior without knowing the groups beforehand.",
                        "ai_followup": "Good explanation. Now, if I gave you a dataset of customer purchases and asked you to predict which customers might churn, how would you approach this problem?"
                    }
                ],
                "coaching_tips": [
                    "Explain your thought process step by step",
                    "Use concrete examples when possible",
                    "Discuss trade-offs and alternative approaches",
                    "Ask clarifying questions about requirements"
                ]
            }
        }
    }
