"""
Simple test FastAPI server
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import asyncio
import io
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Career Coach Test API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    username: str
    firstName: str = ""
    lastName: str = ""
    role: str = "student"

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

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
    simulationId: str
    status: str
    performanceScore: int = 0
    transcript: List[Dict] = []
    feedback: Dict = {}
    startedAt: str = ""
    completedAt: str = ""

class StartSimulationRequest(BaseModel):
    simulation_id: str
    config: Dict = {}

# Mock data
mock_user = {
    "id": "user-123",
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
}

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
    )
]

mock_sessions = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Career Coach Test API is running"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Mock login endpoint"""
    if request.email == "test@example.com" and request.password == "password":
        return LoginResponse(
            access_token="mock-jwt-token-123",
            token_type="bearer",
            user=mock_user
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    """Mock signup endpoint"""
    new_user = {
        "id": f"user-{uuid.uuid4()}",
        "email": request.email,
        "username": request.username,
        "firstName": request.firstName,
        "lastName": request.lastName,
        "role": request.role,
        "profileCompletionScore": 75
    }
    return LoginResponse(
        access_token="mock-jwt-token-456",
        token_type="bearer",
        user=new_user
    )

@app.get("/api/auth/me")
async def get_current_user():
    """Get current user endpoint"""
    return mock_user

@app.get("/api/simulations/available")
async def get_available_simulations():
    """Get available simulations"""
    return mock_simulations

@app.get("/api/simulations/{simulation_id}")
async def get_simulation(simulation_id: str):
    """Get specific simulation"""
    for sim in mock_simulations:
        if sim.id == simulation_id:
            return sim
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.post("/api/simulations/start")
async def start_simulation(request: StartSimulationRequest):
    """Start a simulation session"""
    session_id = str(uuid.uuid4())
    session = SimulationSession(
        id=session_id,
        simulationId=request.simulation_id,
        status="active",
        startedAt="2024-01-01T10:00:00Z"
    )
    mock_sessions[session_id] = session
    return session

@app.get("/api/simulations/session/{session_id}")
async def get_session(session_id: str):
    """Get simulation session"""
    if session_id in mock_sessions:
        return mock_sessions[session_id]
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/simulations/session/{session_id}/end")
async def end_simulation(session_id: str):
    """End simulation session"""
    if session_id in mock_sessions:
        mock_sessions[session_id].status = "completed"
        mock_sessions[session_id].completedAt = "2024-01-01T10:30:00Z"
        return {"message": "Simulation ended successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/simulations/session/{session_id}/pause")
async def pause_simulation(session_id: str):
    """Pause simulation session"""
    if session_id in mock_sessions:
        mock_sessions[session_id].status = "paused"
        return {"message": "Simulation paused successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/simulations/session/{session_id}/resume")
async def resume_simulation(session_id: str):
    """Resume simulation session"""
    if session_id in mock_sessions:
        mock_sessions[session_id].status = "active"
        return {"message": "Simulation resumed successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/voice/voices")
async def get_available_voices():
    """Get available AI voices"""
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "characteristics": ["Neutral", "Clear"]},
            {"id": "echo", "name": "Echo", "characteristics": ["Male", "Warm"]},
            {"id": "nova", "name": "Nova", "characteristics": ["Female", "Energetic"]}
        ]
    }

@app.post("/api/voice/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """Mock speech-to-text transcription"""
    # Simulate processing delay
    await asyncio.sleep(0.5)
    return {
        "text": "This is a mock transcription of your speech. The AI voice system is working perfectly!",
        "confidence": 0.95,
        "language": "en"
    }

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "alloy"
    speed: float = 1.0

@app.post("/api/voice/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """Mock text-to-speech synthesis"""
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    # Create a mock audio file (silence)
    mock_audio_data = b'\x00' * 1000  # 1KB of silence
    
    return Response(
        content=mock_audio_data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "attachment; filename=speech.mp3",
            "Content-Length": str(len(mock_audio_data))
        }
    )

@app.post("/api/voice/simulation/transcribe")
async def simulation_transcribe(audio_file: UploadFile = File(...), session_id: str = Form(...)):
    """Mock simulation speech-to-text"""
    await asyncio.sleep(0.5)
    return {
        "text": "This is a mock transcription for the simulation. The AI coach is listening!",
        "confidence": 0.92,
        "language": "en"
    }

@app.post("/api/voice/simulation/ai-response")
async def simulation_ai_response(text: str = Form(...), session_id: str = Form(...), persona_config: str = Form("{}")):
    """Mock AI response generation"""
    await asyncio.sleep(0.5)
    
    # Create a mock audio file (silence)
    mock_audio_data = b'\x00' * 2000  # 2KB of silence
    
    return Response(
        content=mock_audio_data,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "attachment; filename=ai-response.mp3",
            "Content-Length": str(len(mock_audio_data))
        }
    )

@app.get("/api/career/roadmap")
async def get_career_roadmap(goal: str = "Data Analyst"):
    """Get career roadmap"""
    return {
        "goal": goal,
        "skills": [
            {"name": "Python", "level": "Intermediate", "priority": "High"},
            {"name": "SQL", "level": "Intermediate", "priority": "High"},
            {"name": "Statistics", "level": "Beginner", "priority": "Medium"}
        ],
        "timeline": "6-12 months"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
