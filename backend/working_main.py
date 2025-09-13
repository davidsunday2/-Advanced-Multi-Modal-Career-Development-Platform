"""
Working FastAPI server with mock endpoints for testing
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import asyncio
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Career Coach & Simulator API",
    description="Mock API for testing frontend features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data models
class User(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class Simulation(BaseModel):
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    estimated_duration: int
    skills_developed: List[str]

class SimulationSession(BaseModel):
    id: str
    simulation_id: str
    status: str
    current_step: int
    total_steps: int
    messages: List[Dict[str, Any]]
    created_at: str

class TranscriptionResult(BaseModel):
    text: str
    confidence: float
    language: str

# Mock data
mock_user = User(
    id="user-123",
    email="test@example.com",
    username="testuser",
    first_name="Test",
    last_name="User"
)

mock_simulations = [
    Simulation(
        id="sim-1",
        title="Data Analyst Interview",
        description="Practice answering technical questions about data analysis",
        category="Technical Interview",
        difficulty="Intermediate",
        estimated_duration=30,
        skills_developed=["SQL", "Python", "Statistics", "Communication"]
    ),
    Simulation(
        id="sim-2", 
        title="Stakeholder Presentation",
        description="Present your findings to non-technical stakeholders",
        category="Communication",
        difficulty="Advanced",
        estimated_duration=20,
        skills_developed=["Presentation", "Communication", "Data Visualization"]
    ),
    Simulation(
        id="sim-3",
        title="Code Review Session",
        description="Review and improve code with a senior developer",
        category="Technical",
        difficulty="Intermediate",
        estimated_duration=25,
        skills_developed=["Code Review", "Best Practices", "Collaboration"]
    )
]

mock_sessions = {}

# Authentication request models
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    username: str

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Mock login endpoint"""
    if request.email == "test@example.com" and request.password == "password":
        return LoginResponse(
            access_token="mock-jwt-token-123",
            token_type="bearer",
            user=mock_user
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/signup", response_model=LoginResponse)
async def signup(request: SignupRequest):
    """Mock signup endpoint"""
    return LoginResponse(
        access_token="mock-jwt-token-123",
        token_type="bearer",
        user=User(
            id=str(uuid.uuid4()),
            email=request.email,
            username=request.username
        )
    )

@app.get("/api/auth/me", response_model=User)
async def get_current_user():
    """Mock get current user endpoint"""
    return mock_user

@app.post("/api/auth/refresh")
async def refresh_token():
    """Mock token refresh endpoint"""
    return {"token": "new-mock-jwt-token-456"}

@app.post("/api/auth/logout")
async def logout():
    """Mock logout endpoint"""
    return {"message": "Logged out successfully"}

# Simulations endpoints
@app.get("/api/simulations/available", response_model=List[Simulation])
async def get_available_simulations():
    """Get available simulations"""
    return mock_simulations

@app.get("/api/simulations/{simulation_id}", response_model=Simulation)
async def get_simulation(simulation_id: str):
    """Get specific simulation"""
    for sim in mock_simulations:
        if sim.id == simulation_id:
            return sim
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.post("/api/simulations/{simulation_id}/start", response_model=SimulationSession)
async def start_simulation(simulation_id: str, config: Dict[str, Any] = None):
    """Start a new simulation session"""
    session_id = str(uuid.uuid4())
    session = SimulationSession(
        id=session_id,
        simulation_id=simulation_id,
        status="active",
        current_step=1,
        total_steps=5,
        messages=[
            {
                "role": "assistant",
                "content": f"Welcome to the simulation! Let's begin with the first question.",
                "timestamp": "2024-01-01T10:00:00Z"
            }
        ],
        created_at="2024-01-01T10:00:00Z"
    )
    mock_sessions[session_id] = session
    return session

@app.get("/api/simulations/session/{session_id}", response_model=SimulationSession)
async def get_session(session_id: str):
    """Get simulation session"""
    if session_id in mock_sessions:
        return mock_sessions[session_id]
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/simulations/session/{session_id}/message")
async def send_message(session_id: str, message: str):
    """Send message to simulation"""
    if session_id not in mock_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = mock_sessions[session_id]
    session.messages.append({
        "role": "user",
        "content": message,
        "timestamp": "2024-01-01T10:01:00Z"
    })
    
    # Mock AI response
    ai_response = f"I understand you said: '{message}'. This is a mock response from the AI coach. How would you like to proceed?"
    session.messages.append({
        "role": "assistant", 
        "content": ai_response,
        "timestamp": "2024-01-01T10:01:30Z"
    })
    
    session.current_step += 1
    return {"message": "Message sent successfully", "ai_response": ai_response}

# Voice endpoints
@app.post("/api/voice/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Mock speech-to-text transcription"""
    return TranscriptionResult(
        text="This is a mock transcription of your audio input",
        confidence=0.95,
        language="en"
    )

@app.post("/api/voice/synthesize")
async def synthesize_speech(text: str, voice: str = "alloy"):
    """Mock text-to-speech synthesis"""
    return {"audio_url": "mock-audio-url.mp3", "duration": 5.2}

@app.get("/api/voice/voices")
async def get_available_voices():
    """Get available AI voices"""
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "characteristics": ["Neutral", "Clear"]},
            {"id": "echo", "name": "Echo", "characteristics": ["Male", "Warm"]},
            {"id": "fable", "name": "Fable", "characteristics": ["British", "Narrative"]},
            {"id": "onyx", "name": "Onyx", "characteristics": ["Male", "Deep"]},
            {"id": "nova", "name": "Nova", "characteristics": ["Female", "Energetic"]},
            {"id": "shimmer", "name": "Shimmer", "characteristics": ["Female", "Soft"]}
        ]
    }

# Career endpoints
@app.get("/api/career/roadmap")
async def get_career_roadmap(goal: str = "Data Analyst"):
    """Get career roadmap"""
    return {
        "goal": goal,
        "skills": [
            {"name": "Python", "level": "Intermediate", "priority": "High"},
            {"name": "SQL", "level": "Intermediate", "priority": "High"},
            {"name": "Statistics", "level": "Beginner", "priority": "Medium"},
            {"name": "Data Visualization", "level": "Beginner", "priority": "Medium"}
        ],
        "timeline": "6-12 months",
        "resources": [
            {"title": "Python for Data Science", "type": "Course", "duration": "40 hours"},
            {"title": "SQL Fundamentals", "type": "Course", "duration": "20 hours"}
        ]
    }

@app.get("/api/career/skill-gap")
async def analyze_skill_gap(skills: List[str] = ["Python", "SQL"]):
    """Analyze skill gap"""
    return {
        "current_skills": skills,
        "gaps": ["Statistics", "Machine Learning", "Communication"],
        "recommendations": [
            "Take a statistics course",
            "Practice presenting data findings",
            "Learn basic machine learning concepts"
        ]
    }

# Health and status endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Career Coach API is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AI Career Coach & Simulator API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/auth/*",
            "simulations": "/api/simulations/*",
            "voice": "/api/voice/*",
            "career": "/api/career/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
