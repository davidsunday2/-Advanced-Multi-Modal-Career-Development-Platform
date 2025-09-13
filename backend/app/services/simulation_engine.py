"""
Simulation Engine Service

Implements agentic AI workflows for professional simulation scenarios.
Creates realistic stakeholder meetings, technical interviews, and other scenarios.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from app.core.config import settings
from app.core.exceptions import SimulationError
from app.core.cache import cache

logger = logging.getLogger(__name__)


class SimulationScenario(Enum):
    """Available simulation scenarios"""
    STAKEHOLDER_MEETING = "stakeholder_meeting"
    TECHNICAL_INTERVIEW = "technical_interview"
    BEHAVIORAL_INTERVIEW = "behavioral_interview"
    PRESENTATION = "presentation"
    NEGOTIATION = "negotiation"
    CLIENT_CONSULTATION = "client_consultation"
    CONFLICT_RESOLUTION = "conflict_resolution"


class AIPersona(Enum):
    """AI persona types for different scenarios"""
    NON_TECHNICAL_MANAGER = "non_technical_manager"
    SENIOR_ENGINEER = "senior_engineer"
    HR_REPRESENTATIVE = "hr_representative"
    EXECUTIVE = "executive"
    CLIENT = "client"
    MENTOR = "mentor"


class SimulationEngine:
    """Agentic AI workflow for professional simulations"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model_name=settings.OPENAI_MODEL, temperature=0.7)
        self.active_sessions = {}
    
    async def start_simulation(
        self,
        scenario: SimulationScenario,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Start a new simulation session
        
        Example: Stakeholder Meeting scenario
        """
        try:
            session_id = str(uuid.uuid4())
            
            # Get scenario configuration
            scenario_config = self._get_scenario_config(scenario)
            
            # Initialize AI persona
            persona_config = self._get_persona_config(scenario_config["persona"])
            
            # Create session state
            session_state = {
                "session_id": session_id,
                "user_id": user_id,
                "scenario": scenario.value,
                "persona": persona_config,
                "context": context or {},
                "conversation_history": [],
                "current_phase": "introduction",
                "scenario_state": scenario_config["initial_state"],
                "performance_metrics": {
                    "clarity_score": 0,
                    "technical_accuracy": 0,
                    "communication_effectiveness": 0,
                    "response_relevance": 0
                },
                "started_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
            
            # Generate opening statement
            opening_message = await self._generate_opening_statement(
                scenario_config, persona_config, context
            )
            
            session_state["conversation_history"].append({
                "speaker": "ai",
                "message": opening_message,
                "timestamp": datetime.now().isoformat(),
                "phase": "introduction"
            })
            
            # Store session
            self.active_sessions[session_id] = session_state
            await cache.set(f"simulation_session:{session_id}", session_state, ttl=7200)
            
            logger.info(f"Started simulation session {session_id} for scenario {scenario.value}")
            
            return {
                "session_id": session_id,
                "scenario": scenario.value,
                "ai_persona": persona_config["name"],
                "opening_message": opening_message,
                "instructions": scenario_config["user_instructions"],
                "objectives": scenario_config["learning_objectives"]
            }
            
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            raise SimulationError(f"Simulation startup failed: {str(e)}")
    
    async def process_user_response(
        self,
        session_id: str,
        user_message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Process user response and generate AI reply with feedback
        
        This is the core of the agentic workflow
        """
        try:
            # Get session state
            session_state = await self._get_session_state(session_id)
            if not session_state:
                raise SimulationError("Session not found")
            
            # Add user message to history
            session_state["conversation_history"].append({
                "speaker": "user",
                "message": user_message,
                "timestamp": datetime.now().isoformat(),
                "phase": session_state["current_phase"],
                "type": message_type
            })
            
            # Analyze user response
            response_analysis = await self._analyze_user_response(
                user_message, session_state
            )
            
            # Update performance metrics
            self._update_performance_metrics(session_state, response_analysis)
            
            # Generate AI response based on persona and scenario
            ai_response = await self._generate_ai_response(
                user_message, session_state, response_analysis
            )
            
            # Add AI response to history
            session_state["conversation_history"].append({
                "speaker": "ai",
                "message": ai_response["message"],
                "timestamp": datetime.now().isoformat(),
                "phase": session_state["current_phase"],
                "persona_behavior": ai_response.get("behavior_notes")
            })
            
            # Check if scenario should progress to next phase
            phase_update = await self._check_phase_progression(session_state)
            if phase_update:
                session_state["current_phase"] = phase_update["new_phase"]
                ai_response["phase_transition"] = phase_update
            
            # Update session state
            session_state["last_activity"] = datetime.now().isoformat()
            await cache.set(f"simulation_session:{session_id}", session_state, ttl=7200)
            
            return {
                "ai_response": ai_response["message"],
                "current_phase": session_state["current_phase"],
                "performance_feedback": response_analysis.get("feedback"),
                "phase_transition": phase_update,
                "session_metrics": session_state["performance_metrics"]
            }
            
        except Exception as e:
            logger.error(f"Failed to process user response: {e}")
            raise SimulationError(f"Response processing failed: {str(e)}")
    
    async def end_simulation(self, session_id: str) -> Dict[str, Any]:
        """
        End simulation and provide comprehensive feedback
        """
        try:
            session_state = await self._get_session_state(session_id)
            if not session_state:
                raise SimulationError("Session not found")
            
            # Generate final feedback
            final_feedback = await self._generate_final_feedback(session_state)
            
            # Calculate final scores
            final_scores = self._calculate_final_scores(session_state)
            
            # Mark session as completed
            session_state["status"] = "completed"
            session_state["completed_at"] = datetime.now().isoformat()
            session_state["final_feedback"] = final_feedback
            session_state["final_scores"] = final_scores
            
            # Store completed session
            await cache.set(f"completed_session:{session_id}", session_state, ttl=86400)
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            logger.info(f"Completed simulation session {session_id}")
            
            return {
                "session_id": session_id,
                "final_feedback": final_feedback,
                "final_scores": final_scores,
                "conversation_summary": self._generate_conversation_summary(session_state),
                "improvement_suggestions": final_feedback.get("improvement_suggestions", []),
                "next_steps": final_feedback.get("next_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to end simulation: {e}")
            raise SimulationError(f"Session ending failed: {str(e)}")
    
    def _get_scenario_config(self, scenario: SimulationScenario) -> Dict[str, Any]:
        """Get configuration for specific scenario"""
        
        configs = {
            SimulationScenario.STAKEHOLDER_MEETING: {
                "persona": AIPersona.NON_TECHNICAL_MANAGER,
                "user_instructions": "You've completed your analysis. Present your findings to a non-technical manager who needs to understand the business impact.",
                "learning_objectives": [
                    "Translate technical concepts to business language",
                    "Handle non-technical questions effectively",
                    "Present data in an understandable way",
                    "Address business concerns and objections"
                ],
                "initial_state": {
                    "context": "quarterly_review",
                    "urgency": "medium",
                    "stakeholder_knowledge": "non_technical"
                },
                "phases": ["introduction", "presentation", "questions", "objections", "wrap_up"]
            },
            
            SimulationScenario.TECHNICAL_INTERVIEW: {
                "persona": AIPersona.SENIOR_ENGINEER,
                "user_instructions": "You're in a technical interview. Answer questions clearly and demonstrate your problem-solving approach.",
                "learning_objectives": [
                    "Explain technical concepts clearly",
                    "Demonstrate problem-solving methodology",
                    "Handle technical pressure effectively",
                    "Show depth of understanding"
                ],
                "initial_state": {
                    "difficulty": "intermediate",
                    "focus_area": "problem_solving",
                    "follow_up_depth": "medium"
                },
                "phases": ["warm_up", "technical_questions", "problem_solving", "design_discussion", "conclusion"]
            },
            
            SimulationScenario.BEHAVIORAL_INTERVIEW: {
                "persona": AIPersona.HR_REPRESENTATIVE,
                "user_instructions": "Answer behavioral questions using specific examples from your experience.",
                "learning_objectives": [
                    "Use STAR method effectively",
                    "Provide specific, relevant examples",
                    "Demonstrate soft skills",
                    "Show self-awareness and growth"
                ],
                "initial_state": {
                    "interview_style": "collaborative",
                    "depth": "detailed_examples"
                },
                "phases": ["introduction", "experience_questions", "situational_scenarios", "growth_questions", "closing"]
            }
        }
        
        return configs.get(scenario, configs[SimulationScenario.STAKEHOLDER_MEETING])
    
    def _get_persona_config(self, persona: AIPersona) -> Dict[str, Any]:
        """Get AI persona configuration"""
        
        personas = {
            AIPersona.NON_TECHNICAL_MANAGER: {
                "name": "Sarah Johnson",
                "role": "Product Manager", 
                "personality": "Business-focused, results-oriented, asks for clarification on technical terms",
                "communication_style": "Direct, wants bottom-line impact, skeptical of technical complexity",
                "knowledge_level": "Business strategy, limited technical background",
                "typical_concerns": ["Budget impact", "Timeline", "User experience", "ROI"],
                "response_patterns": [
                    "Asks for business translation of technical points",
                    "Focuses on metrics and outcomes", 
                    "Challenges technical complexity",
                    "Wants clear action items"
                ]
            },
            
            AIPersona.SENIOR_ENGINEER: {
                "name": "Alex Chen",
                "role": "Senior Software Engineer",
                "personality": "Analytical, detail-oriented, values technical depth and clarity",
                "communication_style": "Methodical, probing, wants to understand thought process",
                "knowledge_level": "Deep technical expertise, system design experience",
                "typical_concerns": ["Code quality", "Scalability", "Best practices", "Problem-solving approach"],
                "response_patterns": [
                    "Asks follow-up technical questions",
                    "Explores edge cases and trade-offs",
                    "Evaluates problem-solving methodology",
                    "Tests depth of understanding"
                ]
            },
            
            AIPersona.HR_REPRESENTATIVE: {
                "name": "Jordan Martinez",
                "role": "Senior HR Business Partner",
                "personality": "Empathetic, structured, focused on cultural fit and growth potential",
                "communication_style": "Warm but professional, uses behavioral interviewing techniques",
                "knowledge_level": "People management, organizational psychology, interviewing best practices",
                "typical_concerns": ["Team fit", "Communication skills", "Growth mindset", "Leadership potential"],
                "response_patterns": [
                    "Asks for specific examples using STAR method",
                    "Probes for self-reflection and learning",
                    "Evaluates interpersonal skills",
                    "Explores motivation and values"
                ]
            }
        }
        
        return personas.get(persona, personas[AIPersona.NON_TECHNICAL_MANAGER])
    
    async def _generate_opening_statement(
        self,
        scenario_config: Dict[str, Any],
        persona_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate realistic opening statement for the scenario"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are {persona_name}, a {persona_role}. 
        
        PERSONALITY: {personality}
        COMMUNICATION STYLE: {communication_style}
        
        SCENARIO CONTEXT: {context}
        
        Generate a realistic opening statement to start this simulation. Be natural, professional, and true to your persona. Keep it conversational and set appropriate expectations.
        
        Make it feel like a real workplace interaction.
        """)
        
        chain = prompt | self.llm | StrOutputParser()
        
        opening = await chain.ainvoke({
            "persona_name": persona_config["name"],
            "persona_role": persona_config["role"],
            "personality": persona_config["personality"],
            "communication_style": persona_config["communication_style"],
            "context": context
        })
        
        return opening.strip()
    
    async def _analyze_user_response(
        self,
        user_message: str,
        session_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user response for quality and appropriateness"""
        
        analysis_prompt = ChatPromptTemplate.from_template("""
        Analyze this user response in the context of a {scenario} simulation.
        
        USER RESPONSE: {user_message}
        CURRENT PHASE: {current_phase}
        CONVERSATION HISTORY: {conversation_summary}
        
        Provide analysis in this JSON format:
        {{
            "clarity_score": 8.5,
            "technical_accuracy": 7.0,
            "communication_effectiveness": 9.0,
            "response_relevance": 8.0,
            "strengths": ["Clear explanation", "Good examples"],
            "improvement_areas": ["Could be more specific", "Missing business impact"],
            "feedback": "Good response! You explained the technical concept clearly. Consider adding more business context for a non-technical audience."
        }}
        """)
        
        chain = analysis_prompt | self.llm | StrOutputParser()
        
        conversation_summary = self._get_conversation_summary(session_state)
        
        analysis_response = await chain.ainvoke({
            "scenario": session_state["scenario"],
            "user_message": user_message,
            "current_phase": session_state["current_phase"],
            "conversation_summary": conversation_summary
        })
        
        # Parse JSON response
        import json
        try:
            analysis = json.loads(analysis_response)
        except json.JSONDecodeError:
            # Fallback analysis
            analysis = {
                "clarity_score": 7.0,
                "technical_accuracy": 7.0,
                "communication_effectiveness": 7.0,
                "response_relevance": 7.0,
                "feedback": "Good response. Continue with the conversation."
            }
        
        return analysis
    
    async def _generate_ai_response(
        self,
        user_message: str,
        session_state: Dict[str, Any],
        response_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI response based on persona and scenario state"""
        
        persona = session_state["persona"]
        scenario = session_state["scenario"]
        current_phase = session_state["current_phase"]
        
        response_prompt = ChatPromptTemplate.from_template("""
        You are {persona_name}, a {persona_role} in a {scenario} simulation.
        
        YOUR PERSONALITY: {personality}
        YOUR COMMUNICATION STYLE: {communication_style}
        YOUR TYPICAL CONCERNS: {typical_concerns}
        
        CURRENT PHASE: {current_phase}
        USER JUST SAID: {user_message}
        
        CONVERSATION CONTEXT: {conversation_summary}
        
        RESPONSE ANALYSIS: The user's response scored {clarity_score}/10 for clarity and {communication_effectiveness}/10 for communication effectiveness.
        
        Generate your response as this persona. Stay in character, be realistic, and:
        1. Respond naturally to what the user said
        2. Ask relevant follow-up questions based on your persona's concerns
        3. Challenge appropriately based on your role
        4. Guide the conversation forward
        5. Be supportive but realistic
        
        Keep your response conversational and authentic to your persona.
        """)
        
        chain = response_prompt | self.llm | StrOutputParser()
        
        ai_response = await chain.ainvoke({
            "persona_name": persona["name"],
            "persona_role": persona["role"],
            "scenario": scenario,
            "personality": persona["personality"],
            "communication_style": persona["communication_style"],
            "typical_concerns": ", ".join(persona.get("typical_concerns", [])),
            "current_phase": current_phase,
            "user_message": user_message,
            "conversation_summary": self._get_conversation_summary(session_state),
            "clarity_score": response_analysis.get("clarity_score", 7),
            "communication_effectiveness": response_analysis.get("communication_effectiveness", 7)
        })
        
        return {
            "message": ai_response.strip(),
            "behavior_notes": f"Responded as {persona['name']} in {current_phase} phase"
        }
    
    async def _check_phase_progression(self, session_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if simulation should move to next phase"""
        
        current_phase = session_state["current_phase"]
        conversation_length = len(session_state["conversation_history"])
        
        # Simple phase progression logic (can be enhanced)
        phase_progression = {
            "introduction": {"next": "presentation", "min_exchanges": 2},
            "presentation": {"next": "questions", "min_exchanges": 4},
            "questions": {"next": "objections", "min_exchanges": 6},
            "objections": {"next": "wrap_up", "min_exchanges": 8}
        }
        
        if current_phase in phase_progression:
            phase_info = phase_progression[current_phase]
            if conversation_length >= phase_info["min_exchanges"]:
                return {
                    "new_phase": phase_info["next"],
                    "transition_message": f"Moving to {phase_info['next']} phase"
                }
        
        return None
    
    async def _generate_final_feedback(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive final feedback"""
        
        feedback_prompt = ChatPromptTemplate.from_template("""
        Provide comprehensive feedback for this {scenario} simulation session.
        
        PERFORMANCE METRICS:
        - Clarity: {clarity_score}/10
        - Technical Accuracy: {technical_accuracy}/10
        - Communication: {communication_effectiveness}/10
        - Relevance: {response_relevance}/10
        
        CONVERSATION SUMMARY: {conversation_summary}
        
        Provide feedback in this JSON format:
        {{
            "overall_summary": "Overall performance summary",
            "strengths": ["Strength 1", "Strength 2"],
            "improvement_areas": ["Area 1", "Area 2"],
            "specific_feedback": {{
                "communication": "Communication-specific feedback",
                "technical_content": "Technical content feedback",
                "professional_presence": "Professional presence feedback"
            }},
            "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
            "next_steps": ["Next step 1", "Next step 2"]
        }}
        """)
        
        chain = feedback_prompt | self.llm | StrOutputParser()
        
        metrics = session_state["performance_metrics"]
        
        feedback_response = await chain.ainvoke({
            "scenario": session_state["scenario"],
            "clarity_score": metrics.get("clarity_score", 0),
            "technical_accuracy": metrics.get("technical_accuracy", 0),
            "communication_effectiveness": metrics.get("communication_effectiveness", 0),
            "response_relevance": metrics.get("response_relevance", 0),
            "conversation_summary": self._get_conversation_summary(session_state)
        })
        
        import json
        try:
            feedback = json.loads(feedback_response)
        except json.JSONDecodeError:
            feedback = {
                "overall_summary": "Good simulation session completed",
                "strengths": ["Active participation", "Professional communication"],
                "improvement_areas": ["Continue practicing", "Focus on specific examples"],
                "improvement_suggestions": ["Practice more scenarios", "Work on clarity"],
                "next_steps": ["Try advanced simulations", "Get additional feedback"]
            }
        
        return feedback
    
    def _update_performance_metrics(self, session_state: Dict[str, Any], analysis: Dict[str, Any]):
        """Update session performance metrics"""
        metrics = session_state["performance_metrics"]
        
        # Update with weighted average
        weight = 0.3  # New response weight
        metrics["clarity_score"] = (metrics["clarity_score"] * (1-weight) + 
                                   analysis.get("clarity_score", 7) * weight)
        metrics["technical_accuracy"] = (metrics["technical_accuracy"] * (1-weight) + 
                                        analysis.get("technical_accuracy", 7) * weight)
        metrics["communication_effectiveness"] = (metrics["communication_effectiveness"] * (1-weight) + 
                                                 analysis.get("communication_effectiveness", 7) * weight)
        metrics["response_relevance"] = (metrics["response_relevance"] * (1-weight) + 
                                        analysis.get("response_relevance", 7) * weight)
    
    def _calculate_final_scores(self, session_state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate final performance scores"""
        metrics = session_state["performance_metrics"]
        
        overall_score = (
            metrics["clarity_score"] * 0.25 +
            metrics["technical_accuracy"] * 0.25 +
            metrics["communication_effectiveness"] * 0.30 +
            metrics["response_relevance"] * 0.20
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "clarity": round(metrics["clarity_score"], 1),
            "technical_accuracy": round(metrics["technical_accuracy"], 1),
            "communication": round(metrics["communication_effectiveness"], 1),
            "relevance": round(metrics["response_relevance"], 1)
        }
    
    def _get_conversation_summary(self, session_state: Dict[str, Any]) -> str:
        """Get summary of conversation for context"""
        history = session_state["conversation_history"]
        if len(history) <= 4:
            return "Early in conversation"
        
        last_messages = history[-4:]
        summary = ""
        for msg in last_messages:
            speaker = "User" if msg["speaker"] == "user" else "AI"
            summary += f"{speaker}: {msg['message'][:50]}... "
        
        return summary
    
    def _generate_conversation_summary(self, session_state: Dict[str, Any]) -> str:
        """Generate full conversation summary"""
        history = session_state["conversation_history"]
        summary = f"Simulation: {session_state['scenario']}\n"
        summary += f"Duration: {len(history)} exchanges\n"
        summary += f"Phases covered: {session_state['current_phase']}\n"
        return summary
    
    async def _get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state from cache or memory"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        cached_state = await cache.get(f"simulation_session:{session_id}")
        if cached_state:
            self.active_sessions[session_id] = cached_state
            return cached_state
        
        return None
