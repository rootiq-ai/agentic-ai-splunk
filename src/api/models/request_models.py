"""Pydantic models for API requests and responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

class NaturalLanguageQueryRequest(BaseModel):
    """Request model for natural language queries."""
    
    question: str = Field(..., description="Natural language question", min_length=5, max_length=1000)
    max_results: int = Field(100, description="Maximum number of results", ge=1, le=10000)
    
    @validator('question')
    def validate_question(cls, v):
        """Validate question field."""
        if not v.strip():
            raise ValueError("Question cannot be empty or whitespace only")
        return v.strip()

class SPLQueryRequest(BaseModel):
    """Request model for direct SPL queries."""
    
    spl_query: str = Field(..., description="SPL query string", min_length=5, max_length=5000)
    max_results: int = Field(100, description="Maximum number of results", ge=1, le=10000)
    
    @validator('spl_query')
    def validate_spl_query(cls, v):
        """Validate SPL query field."""
        if not v.strip():
            raise ValueError("SPL query cannot be empty or whitespace only")
        return v.strip()

class QueryEnhancementRequest(BaseModel):
    """Request model for query enhancement."""
    
    spl_query: str = Field(..., description="Original SPL query", min_length=5, max_length=5000)
    feedback: str = Field(..., description="Enhancement feedback", min_length=5, max_length=500)
    
    @validator('spl_query', 'feedback')
    def validate_fields(cls, v):
        """Validate string fields."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

class QuerySuggestionRequest(BaseModel):
    """Request model for query suggestions."""
    
    partial_question: str = Field("", description="Partial question text", max_length=100)
    max_suggestions: int = Field(5, description="Maximum number of suggestions", ge=1, le=20)

# Response Models

class SPLValidationResponse(BaseModel):
    """Response model for SPL validation."""
    
    valid: bool = Field(..., description="Whether the SPL is valid")
    query: str = Field(..., description="The validated query")
    error: Optional[str] = Field(None, description="Validation error message")

class QueryStatistics(BaseModel):
    """Model for query execution statistics."""
    
    result_count: int = Field(..., description="Number of results returned")
    scan_count: int = Field(0, description="Number of events scanned")
    run_duration: float = Field(0.0, description="Query execution time in seconds")
    search_id: Optional[str] = Field(None, description="Splunk search job ID")

class NaturalLanguageQueryResponse(BaseModel):
    """Response model for natural language queries."""
    
    success: bool = Field(..., description="Whether the query was successful")
    question: str = Field(..., description="Original question")
    spl_query: str = Field("", description="Generated SPL query")
    explanation: str = Field("", description="Explanation of the query")
    confidence: str = Field("medium", description="Confidence level: high|medium|low")
    results: List[Dict[str, Any]] = Field([], description="Query results")
    result_count: int = Field(0, description="Number of results")
    statistics: QueryStatistics = Field(default_factory=QueryStatistics)
    validation: SPLValidationResponse = Field(default_factory=SPLValidationResponse)
    processing_time: float = Field(0.0, description="Total processing time")
    error: Optional[str] = Field(None, description="Error message if failed")

class SPLQueryResponse(BaseModel):
    """Response model for SPL queries."""
    
    success: bool = Field(..., description="Whether the query was successful")
    spl_query: str = Field(..., description="Executed SPL query")
    results: List[Dict[str, Any]] = Field([], description="Query results")
    result_count: int = Field(0, description="Number of results")
    statistics: QueryStatistics = Field(default_factory=QueryStatistics)
    validation: SPLValidationResponse = Field(default_factory=SPLValidationResponse)
    processing_time: float = Field(0.0, description="Processing time")
    error: Optional[str] = Field(None, description="Error message if failed")

class QueryEnhancementResponse(BaseModel):
    """Response model for query enhancement."""
    
    success: bool = Field(..., description="Whether enhancement was successful")
    original_query: str = Field(..., description="Original SPL query")
    enhanced_query: str = Field("", description="Enhanced SPL query")
    changes: str = Field("", description="Description of changes made")
    confidence: str = Field("medium", description="Confidence in enhancement")
    error: Optional[str] = Field(None, description="Error message if failed")

class QuerySuggestionResponse(BaseModel):
    """Response model for query suggestions."""
    
    suggestions: List[str] = Field([], description="List of suggested questions")
    partial_question: str = Field("", description="Original partial question")

class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: float = Field(..., description="Health check timestamp")
    services: Dict[str, Any] = Field({}, description="Individual service statuses")

class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: float = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
