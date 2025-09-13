"""
Voice Processing Service

Handles speech-to-text and text-to-speech operations using OpenAI's APIs.
Provides immersive voice capabilities for simulations.
"""

import os
import io
import uuid
import asyncio
import logging
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path

import httpx
from openai import OpenAI
from pydub import AudioSegment
from pydub.effects import normalize

from app.core.config import settings
from app.core.exceptions import VoiceProcessingError, ExternalAPIError
from app.core.cache import cache

logger = logging.getLogger(__name__)


class VoiceService:
    """Comprehensive voice processing service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supported_audio_formats = {
            'wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm', 'flac'
        }
        self.max_audio_duration = settings.MAX_AUDIO_DURATION_SECONDS
        self.audio_sample_rate = settings.AUDIO_SAMPLE_RATE
        
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert speech to text using OpenAI Whisper
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., 'en', 'es')
            prompt: Optional context prompt for better accuracy
            session_id: Session ID for context caching
            
        Returns:
            Dict containing transcription and metadata
        """
        try:
            # Process and validate audio
            processed_audio = await self._preprocess_audio(audio_data)
            
            # Create temporary file for Whisper API
            temp_file_path = self._create_temp_audio_file(processed_audio)
            
            try:
                # Call OpenAI Whisper API
                with open(temp_file_path, 'rb') as audio_file:
                    transcript = await asyncio.to_thread(
                        self.client.audio.transcriptions.create,
                        model=settings.OPENAI_WHISPER_MODEL,
                        file=audio_file,
                        language=language,
                        prompt=prompt,
                        response_format="verbose_json",
                        temperature=0.2
                    )
                
                # Extract results
                result = {
                    "text": transcript.text,
                    "language": transcript.language if hasattr(transcript, 'language') else language,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                    "confidence": self._calculate_confidence(transcript),
                    "segments": getattr(transcript, 'segments', []),
                    "session_id": session_id
                }
                
                # Cache result for context
                if session_id:
                    await self._cache_transcription_context(session_id, result)
                
                logger.info(f"Speech-to-text successful: {len(result['text'])} characters")
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            raise VoiceProcessingError(f"Failed to transcribe audio: {str(e)}")
    
    async def text_to_speech(
        self, 
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
        response_format: str = "mp3",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)
            response_format: Audio format (mp3, opus, aac, flac)
            session_id: Session ID for voice consistency
            
        Returns:
            Dict containing audio data and metadata
        """
        try:
            # Validate inputs
            if not text.strip():
                raise VoiceProcessingError("Text cannot be empty")
            
            if len(text) > 4096:
                logger.warning(f"Text length {len(text)} exceeds recommended limit")
            
            # Get voice preference from session cache
            if session_id:
                cached_voice = await cache.get(f"voice_preference:{session_id}")
                if cached_voice:
                    voice = cached_voice
            
            # Call OpenAI TTS API
            response = await asyncio.to_thread(
                self.client.audio.speech.create,
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format=response_format
            )
            
            # Get audio data
            audio_data = response.content
            
            # Process audio for optimization
            processed_audio = await self._postprocess_audio(audio_data, response_format)
            
            result = {
                "audio_data": processed_audio,
                "format": response_format,
                "voice": voice,
                "model": model,
                "speed": speed,
                "text_length": len(text),
                "audio_duration": await self._estimate_audio_duration(text, speed),
                "session_id": session_id
            }
            
            # Cache voice preference
            if session_id:
                await cache.set(f"voice_preference:{session_id}", voice, ttl=3600)
            
            logger.info(f"Text-to-speech successful: {len(text)} chars -> {len(audio_data)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            raise VoiceProcessingError(f"Failed to generate speech: {str(e)}")
    
    async def process_voice_message(
        self,
        audio_data: bytes,
        session_id: str,
        simulation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete voice message processing for simulations
        
        Args:
            audio_data: Raw audio from user
            session_id: Simulation session ID
            simulation_context: Context for better processing
            
        Returns:
            Dict containing transcription and processing metadata
        """
        try:
            # Prepare context prompt from simulation
            prompt = self._build_context_prompt(simulation_context)
            
            # Transcribe audio
            transcription = await self.speech_to_text(
                audio_data=audio_data,
                prompt=prompt,
                session_id=session_id
            )
            
            # Enhance transcription with context
            enhanced_result = await self._enhance_transcription(
                transcription, simulation_context
            )
            
            # Store in session context
            await self._update_session_voice_context(session_id, enhanced_result)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Voice message processing failed: {e}")
            raise VoiceProcessingError(f"Failed to process voice message: {str(e)}")
    
    async def generate_simulation_response(
        self,
        response_text: str,
        session_id: str,
        persona_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate voice response for simulation AI persona
        
        Args:
            response_text: AI response text
            session_id: Simulation session ID
            persona_config: AI persona voice configuration
            
        Returns:
            Dict containing audio response and metadata
        """
        try:
            # Get persona voice settings
            voice_config = self._get_persona_voice_config(persona_config)
            
            # Generate speech with persona voice
            speech_result = await self.text_to_speech(
                text=response_text,
                voice=voice_config.get('voice', 'alloy'),
                model=voice_config.get('model', 'tts-1'),
                speed=voice_config.get('speed', 1.0),
                session_id=session_id
            )
            
            # Add persona metadata
            speech_result.update({
                'persona_voice': voice_config.get('voice'),
                'persona_style': voice_config.get('style', 'professional'),
                'response_type': voice_config.get('response_type', 'conversational')
            })
            
            return speech_result
            
        except Exception as e:
            logger.error(f"Simulation response generation failed: {e}")
            raise VoiceProcessingError(f"Failed to generate simulation response: {str(e)}")
    
    async def _preprocess_audio(self, audio_data: bytes) -> bytes:
        """Preprocess audio for optimal recognition"""
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            
            # Validate duration
            duration_seconds = len(audio) / 1000
            if duration_seconds > self.max_audio_duration:
                raise VoiceProcessingError(f"Audio too long: {duration_seconds}s (max: {self.max_audio_duration}s)")
            
            # Normalize audio
            audio = normalize(audio)
            
            # Ensure proper format
            audio = audio.set_frame_rate(self.audio_sample_rate)
            audio = audio.set_channels(1)  # Mono
            
            # Export as WAV for Whisper
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format="wav")
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise VoiceProcessingError(f"Failed to preprocess audio: {str(e)}")
    
    async def _postprocess_audio(self, audio_data: bytes, format: str) -> bytes:
        """Postprocess generated audio for optimization"""
        try:
            if format == 'mp3':
                # Load and optimize MP3
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                
                # Normalize volume
                audio = normalize(audio)
                
                # Export optimized
                output_buffer = io.BytesIO()
                audio.export(
                    output_buffer, 
                    format="mp3", 
                    bitrate="128k",
                    parameters=["-q:a", "2"]
                )
                return output_buffer.getvalue()
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"Audio postprocessing failed, using original: {e}")
            return audio_data
    
    def _create_temp_audio_file(self, audio_data: bytes) -> str:
        """Create temporary audio file for API calls"""
        temp_dir = Path(settings.TEMP_PATH)
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / f"audio_{uuid.uuid4().hex}.wav"
        
        with open(temp_file_path, 'wb') as f:
            f.write(audio_data)
        
        return str(temp_file_path)
    
    def _calculate_confidence(self, transcript) -> float:
        """Calculate confidence score from Whisper response"""
        # Whisper doesn't provide confidence directly
        # Use heuristics based on transcript quality
        if hasattr(transcript, 'segments') and transcript.segments:
            # Average confidence from segments if available
            confidences = [
                getattr(seg, 'avg_logprob', -1.0) 
                for seg in transcript.segments
            ]
            if confidences:
                # Convert log probability to confidence (0-1)
                avg_logprob = sum(confidences) / len(confidences)
                return max(0.0, min(1.0, (avg_logprob + 1.0)))
        
        # Fallback confidence based on text quality
        text = transcript.text.strip()
        if not text:
            return 0.0
        elif len(text) < 10:
            return 0.7
        else:
            return 0.85
    
    async def _estimate_audio_duration(self, text: str, speed: float) -> float:
        """Estimate audio duration based on text and speed"""
        # Average speaking rate: ~150 words per minute
        words = len(text.split())
        base_duration = (words / 150) * 60  # seconds
        return base_duration / speed
    
    def _build_context_prompt(self, simulation_context: Optional[Dict[str, Any]]) -> Optional[str]:
        """Build context prompt for better transcription accuracy"""
        if not simulation_context:
            return None
        
        context_parts = []
        
        if 'scenario_type' in simulation_context:
            context_parts.append(f"Scenario: {simulation_context['scenario_type']}")
        
        if 'topic' in simulation_context:
            context_parts.append(f"Topic: {simulation_context['topic']}")
        
        if 'vocabulary' in simulation_context:
            vocab = simulation_context['vocabulary'][:10]  # Limit vocabulary
            context_parts.append(f"Keywords: {', '.join(vocab)}")
        
        return '. '.join(context_parts) if context_parts else None
    
    async def _enhance_transcription(
        self, 
        transcription: Dict[str, Any], 
        simulation_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance transcription with simulation context"""
        enhanced = transcription.copy()
        
        # Add context-aware confidence adjustment
        if simulation_context and 'technical_terms' in simulation_context:
            text = transcription['text'].lower()
            technical_matches = sum(
                1 for term in simulation_context['technical_terms'] 
                if term.lower() in text
            )
            if technical_matches > 0:
                enhanced['confidence'] = min(1.0, enhanced['confidence'] + 0.1)
                enhanced['technical_terms_detected'] = technical_matches
        
        return enhanced
    
    async def _cache_transcription_context(self, session_id: str, transcription: Dict[str, Any]):
        """Cache transcription for session context"""
        cache_key = f"voice_context:{session_id}"
        
        # Get existing context
        existing_context = await cache.get(cache_key) or []
        
        # Add new transcription
        context_entry = {
            'text': transcription['text'],
            'timestamp': transcription.get('timestamp'),
            'confidence': transcription['confidence']
        }
        existing_context.append(context_entry)
        
        # Keep only last 10 entries
        existing_context = existing_context[-10:]
        
        # Cache updated context
        await cache.set(cache_key, existing_context, ttl=3600)
    
    async def _update_session_voice_context(self, session_id: str, transcription: Dict[str, Any]):
        """Update session voice context for continuity"""
        context_key = f"session_voice:{session_id}"
        
        context = {
            'last_transcription': transcription['text'],
            'average_confidence': transcription['confidence'],
            'message_count': 1,
            'updated_at': transcription.get('timestamp')
        }
        
        # Merge with existing context
        existing = await cache.get(context_key)
        if existing:
            context['message_count'] = existing.get('message_count', 0) + 1
            context['average_confidence'] = (
                existing.get('average_confidence', 0.5) + transcription['confidence']
            ) / 2
        
        await cache.set(context_key, context, ttl=7200)
    
    def _get_persona_voice_config(self, persona_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get voice configuration for AI persona"""
        default_config = {
            'voice': 'alloy',
            'model': 'tts-1',
            'speed': 1.0,
            'style': 'professional'
        }
        
        if not persona_config:
            return default_config
        
        # Map persona types to voice characteristics
        persona_voice_map = {
            'technical_interviewer': {
                'voice': 'echo',
                'speed': 0.9,
                'style': 'analytical'
            },
            'stakeholder_manager': {
                'voice': 'nova',
                'speed': 1.1,
                'style': 'executive'
            },
            'mentor_coach': {
                'voice': 'alloy',
                'speed': 0.95,
                'style': 'supportive'
            },
            'client_representative': {
                'voice': 'shimmer',
                'speed': 1.0,
                'style': 'professional'
            }
        }
        
        persona_type = persona_config.get('type', 'professional')
        voice_config = persona_voice_map.get(persona_type, default_config)
        
        # Override with specific config if provided
        if 'voice_config' in persona_config:
            voice_config.update(persona_config['voice_config'])
        
        return voice_config


# Global voice service instance
voice_service = VoiceService()
