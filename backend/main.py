"""
AI Career Coach & Simulator - Main FastAPI Application

This is the entry point for the AI Career Coach & Simulator backend.
It provides APIs for career guidance, skill assessment, and professional simulations.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import auth, users, career, simulations, voice, analytics
from app.core.exceptions import CareerCoachException
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting AI Career Coach & Simulator...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize AI services
    from app.services.ai_service import AIService
    ai_service = AIService()
    await ai_service.initialize()
    logger.info("✅ AI services initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Career Coach & Simulator...")

# Create FastAPI app with comprehensive configuration
app = FastAPI(
    title="AI Career Coach & Simulator API",
    description="""
    Advanced AI-powered career coaching platform that provides personalized guidance, 
    skill-gap analysis, and immersive professional simulations.
    
    ## Features
    
    * **Career Pathfinding**: Personalized career roadmaps based on AI analysis
    * **Skill Assessment**: Comprehensive skill gap analysis with market data
    * **Professional Simulations**: Interactive scenarios for real-world practice
    * **Voice Integration**: Multi-modal interactions with speech capabilities
    * **Progress Tracking**: Detailed analytics and performance insights
    
    ## Authentication
    
    This API uses JWT tokens for authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_jwt_token>
    ```
    """,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and token management"
        },
        {
            "name": "Career",
            "description": "Career path analysis and recommendations"
        },
        {
            "name": "Simulations", 
            "description": "Professional scenario simulations and practice"
        },
        {
            "name": "Voice",
            "description": "Speech-to-text and text-to-speech capabilities"
        },
        {
            "name": "Analytics",
            "description": "Progress tracking and performance insights"
        }
    ]
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(CareerCoachException)
async def career_coach_exception_handler(request, exc: CareerCoachException):
    """Handle custom application exceptions"""
    logger.error(f"CareerCoachException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": exc.__class__.__name__}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Career Coach & Simulator API",
        "version": "1.0.0",
        "status": "healthy",
        "features": {
            "voice_enabled": settings.ENABLE_VOICE_FEATURES,
            "simulations_enabled": settings.ENABLE_SIMULATION_ENGINE,
            "analytics_enabled": settings.ENABLE_CAREER_ANALYTICS
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    try:
        # Check database connection
        from app.core.database import get_db_session
        async with get_db_session() as db:
            await db.execute("SELECT 1")
        
        # Check Redis connection
        from app.core.cache import get_redis
        redis = await get_redis()
        await redis.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "cache": "connected",
            "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(career.router, prefix="/api/v1/career", tags=["Career"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["Simulations"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

# WebSocket endpoint for real-time simulations
@app.websocket("/ws/simulation/{simulation_id}")
async def simulation_websocket(websocket, simulation_id: str):
    """WebSocket endpoint for real-time simulation interactions"""
    from app.services.simulation_websocket import SimulationWebSocketManager
    
    manager = SimulationWebSocketManager()
    await manager.connect(websocket, simulation_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(simulation_id, data)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(simulation_id)

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
