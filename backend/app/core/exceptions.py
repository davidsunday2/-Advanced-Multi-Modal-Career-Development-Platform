"""
Custom Exception Classes

Defines custom exceptions for the AI Career Coach application.
"""

from typing import Any, Dict, Optional


class CareerCoachException(Exception):
    """Base exception for Career Coach application"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers
        super().__init__(detail)


class AuthenticationError(CareerCoachException):
    """Authentication related errors"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=401)


class AuthorizationError(CareerCoachException):
    """Authorization related errors"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=403)


class ValidationError(CareerCoachException):
    """Input validation errors"""
    
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(detail=detail, status_code=422)


class NotFoundError(CareerCoachException):
    """Resource not found errors"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404)


class ConflictError(CareerCoachException):
    """Resource conflict errors"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=409)


class AIServiceError(CareerCoachException):
    """AI service related errors"""
    
    def __init__(self, detail: str = "AI service error"):
        super().__init__(detail=detail, status_code=503)


class DatabaseError(CareerCoachException):
    """Database related errors"""
    
    def __init__(self, detail: str = "Database error"):
        super().__init__(detail=detail, status_code=500)


class ExternalAPIError(CareerCoachException):
    """External API related errors"""
    
    def __init__(self, detail: str = "External API error"):
        super().__init__(detail=detail, status_code=502)


class RateLimitError(CareerCoachException):
    """Rate limiting errors"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=429)


class FileProcessingError(CareerCoachException):
    """File processing errors"""
    
    def __init__(self, detail: str = "File processing error"):
        super().__init__(detail=detail, status_code=400)


class VoiceProcessingError(CareerCoachException):
    """Voice processing errors"""
    
    def __init__(self, detail: str = "Voice processing error"):
        super().__init__(detail=detail, status_code=400)


class SimulationError(CareerCoachException):
    """Simulation related errors"""
    
    def __init__(self, detail: str = "Simulation error"):
        super().__init__(detail=detail, status_code=500)
