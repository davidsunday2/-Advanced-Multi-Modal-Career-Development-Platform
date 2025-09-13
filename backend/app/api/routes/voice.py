"""
Voice API Routes

Provides endpoints for speech-to-text and text-to-speech operations
with simulation integration for immersive voice experiences.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io

from app.services.voice_service import voice_service
from app.core.exceptions import VoiceProcessingError, ValidationError
from app.api.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech conversion"""
    text: str = Field(..., min_length=1, max_length=4096, description="Text to convert to speech")
    voice: str = Field("alloy", description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)")
    model: str = Field("tts-1", description="TTS model (tts-1 or tts-1-hd)")
    speed: float = Field(1.0, ge=0.25, le=4.0, description="Speech speed")
    response_format: str = Field("mp3", description="Audio format (mp3, opus, aac, flac)")
    session_id: Optional[str] = Field(None, description="Session ID for voice consistency")


class SpeechToTextResponse(BaseModel):
    """Response model for speech-to-text conversion"""
    text: str
    language: Optional[str]
    duration: Optional[float]
    confidence: float
    session_id: Optional[str]
    technical_terms_detected: Optional[int] = None


class VoiceMessageRequest(BaseModel):
    """Request model for simulation voice messages"""
    session_id: str = Field(..., description="Simulation session ID")
    simulation_context: Optional[Dict[str, Any]] = Field(None, description="Simulation context")


class SimulationVoiceResponse(BaseModel):
    """Request model for generating simulation AI responses"""
    text: str = Field(..., description="AI response text")
    session_id: str = Field(..., description="Simulation session ID")
    persona_config: Optional[Dict[str, Any]] = Field(None, description="AI persona configuration")


# Voice Processing Endpoints

@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es')"),
    prompt: Optional[str] = Form(None, description="Context prompt for better accuracy"),
    session_id: Optional[str] = Form(None, description="Session ID for context"),
    current_user: User = Depends(get_current_user)
):
    """
    Convert speech to text using OpenAI Whisper
    
    - **audio_file**: Audio file in supported format (wav, mp3, mp4, m4a, ogg, webm, flac)
    - **language**: Optional language code for better accuracy
    - **prompt**: Optional context prompt to improve transcription
    - **session_id**: Optional session ID for context caching
    """
    try:
        # Validate file type
        if not audio_file.content_type or not any(
            fmt in audio_file.content_type.lower() 
            for fmt in ['audio', 'video']
        ):
            raise ValidationError("File must be an audio or video file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise ValidationError("Audio file is empty")
        
        # Process speech-to-text
        result = await voice_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            prompt=prompt,
            session_id=session_id
        )
        
        logger.info(f"Speech-to-text completed for user {current_user.id}")
        
        return SpeechToTextResponse(**result)
        
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in speech-to-text: {e}")
        raise HTTPException(status_code=500, detail="Speech processing failed")


@router.post("/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech using OpenAI TTS
    
    Returns audio stream that can be played directly by the client.
    
    **Available voices:**
    - **alloy**: Neutral, balanced voice
    - **echo**: Clear, slightly robotic voice  
    - **fable**: Warm, expressive voice
    - **onyx**: Deep, authoritative voice
    - **nova**: Bright, energetic voice
    - **shimmer**: Soft, gentle voice
    """
    try:
        # Generate speech
        result = await voice_service.text_to_speech(
            text=request.text,
            voice=request.voice,
            model=request.model,
            speed=request.speed,
            response_format=request.response_format,
            session_id=request.session_id
        )
        
        # Create streaming response
        audio_stream = io.BytesIO(result['audio_data'])
        
        # Set appropriate content type
        content_type_map = {
            'mp3': 'audio/mpeg',
            'opus': 'audio/opus',
            'aac': 'audio/aac',
            'flac': 'audio/flac'
        }
        content_type = content_type_map.get(request.response_format, 'audio/mpeg')
        
        logger.info(f"Text-to-speech completed for user {current_user.id}")
        
        return StreamingResponse(
            io.BytesIO(result['audio_data']),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{request.response_format}",
                "X-Audio-Duration": str(result.get('audio_duration', 0)),
                "X-Voice-Used": result['voice'],
                "X-Model-Used": result['model']
            }
        )
        
    except VoiceProcessingError as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail="Speech generation failed")


# Simulation-Specific Voice Endpoints

@router.post("/simulation/voice-message", response_model=SpeechToTextResponse)
async def process_simulation_voice_message(
    request: VoiceMessageRequest,
    audio_file: UploadFile = File(..., description="Voice message audio"),
    current_user: User = Depends(get_current_user)
):
    """
    Process voice message within a simulation context
    
    This endpoint provides enhanced transcription accuracy by using
    simulation context for better speech recognition.
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise ValidationError("Audio file is empty")
        
        # Process with simulation context
        result = await voice_service.process_voice_message(
            audio_data=audio_data,
            session_id=request.session_id,
            simulation_context=request.simulation_context
        )
        
        logger.info(f"Simulation voice message processed for session {request.session_id}")
        
        return SpeechToTextResponse(**result)
        
    except VoiceProcessingError as e:
        logger.error(f"Simulation voice processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in simulation voice processing: {e}")
        raise HTTPException(status_code=500, detail="Simulation voice processing failed")


@router.post("/simulation/ai-response")
async def generate_simulation_ai_response(
    request: SimulationVoiceResponse,
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI voice response for simulation persona
    
    Creates realistic voice responses from AI personas with
    appropriate voice characteristics and speaking style.
    """
    try:
        # Generate AI voice response
        result = await voice_service.generate_simulation_response(
            response_text=request.text,
            session_id=request.session_id,
            persona_config=request.persona_config
        )
        
        # Create streaming response
        content_type = 'audio/mpeg'  # Default to MP3
        
        logger.info(f"AI voice response generated for session {request.session_id}")
        
        return StreamingResponse(
            io.BytesIO(result['audio_data']),
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=ai_response.mp3",
                "X-Audio-Duration": str(result.get('audio_duration', 0)),
                "X-Persona-Voice": result.get('persona_voice', 'alloy'),
                "X-Persona-Style": result.get('persona_style', 'professional'),
                "X-Response-Type": result.get('response_type', 'conversational')
            }
        )
        
    except VoiceProcessingError as e:
        logger.error(f"AI voice response error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in AI voice response: {e}")
        raise HTTPException(status_code=500, detail="AI voice response generation failed")


# Voice Configuration and Status Endpoints

@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices and their characteristics
    """
    voices = [
        {
            "id": "alloy",
            "name": "Alloy",
            "description": "Neutral, balanced voice suitable for professional conversations",
            "characteristics": ["neutral", "clear", "professional"],
            "recommended_for": ["interviews", "presentations", "general use"]
        },
        {
            "id": "echo",
            "name": "Echo", 
            "description": "Clear, slightly robotic voice ideal for technical discussions",
            "characteristics": ["clear", "analytical", "precise"],
            "recommended_for": ["technical interviews", "coding discussions"]
        },
        {
            "id": "fable",
            "name": "Fable",
            "description": "Warm, expressive voice great for mentoring and coaching",
            "characteristics": ["warm", "expressive", "supportive"],
            "recommended_for": ["coaching", "mentoring", "feedback sessions"]
        },
        {
            "id": "onyx",
            "name": "Onyx",
            "description": "Deep, authoritative voice perfect for leadership scenarios",
            "characteristics": ["authoritative", "confident", "executive"],
            "recommended_for": ["executive meetings", "leadership discussions"]
        },
        {
            "id": "nova",
            "name": "Nova",
            "description": "Bright, energetic voice ideal for creative and collaborative work",
            "characteristics": ["energetic", "creative", "collaborative"],
            "recommended_for": ["brainstorming", "team meetings", "creative sessions"]
        },
        {
            "id": "shimmer",
            "name": "Shimmer",
            "description": "Soft, gentle voice excellent for customer service scenarios",
            "characteristics": ["gentle", "customer-focused", "empathetic"],
            "recommended_for": ["customer service", "client meetings", "support"]
        }
    ]
    
    return {
        "voices": voices,
        "default_voice": "alloy",
        "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
        "supported_formats": ["mp3", "opus", "aac", "flac"],
        "models": [
            {
                "id": "tts-1",
                "name": "Standard TTS",
                "description": "Fast, efficient text-to-speech",
                "latency": "low"
            },
            {
                "id": "tts-1-hd",
                "name": "HD TTS", 
                "description": "Higher quality text-to-speech",
                "latency": "medium"
            }
        ]
    }


@router.get("/session/{session_id}/voice-stats")
async def get_session_voice_stats(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get voice interaction statistics for a simulation session
    """
    try:
        # This would typically fetch from database
        # For now, return mock stats structure
        stats = {
            "session_id": session_id,
            "total_voice_messages": 0,
            "total_duration_seconds": 0,
            "average_confidence": 0.0,
            "voice_preference": "alloy",
            "interaction_quality": "excellent",
            "technical_terms_detected": 0,
            "last_interaction": None
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching voice stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch voice statistics")
