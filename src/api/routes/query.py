"""API routes for query operations."""

import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from src.api.models.request_models import (
    NaturalLanguageQueryRequest,
    SPLQueryRequest,
    QueryEnhancementRequest,
    QuerySuggestionRequest,
    NaturalLanguageQueryResponse,
    SPLQueryResponse,
    QueryEnhancementResponse,
    QuerySuggestionResponse,
    HealthResponse,
    ErrorResponse
)
from src.core.query_processor import QueryProcessor
from src.utils.logger import get_logger, log_request, log_response, log_error
from src.utils.validators import (
    validate_natural_language_question,
    validate_spl_query,
    validate_max_results
)

# Initialize router and logger
router = APIRouter(prefix="/api/v1/query", tags=["queries"])
logger = get_logger(__name__)

# Global query processor instance
query_processor = None

def get_query_processor() -> QueryProcessor:
    """Get or create query processor instance."""
    global query_processor
    if query_processor is None:
        query_processor = QueryProcessor()
    return query_processor

@router.post("/natural", response_model=NaturalLanguageQueryResponse)
async def query_natural_language(request: NaturalLanguageQueryRequest):
    """
    Convert natural language question to SPL and execute.
    
    This endpoint takes a natural language question, converts it to SPL using OpenAI,
    and executes the query against Splunk.
    """
    start_time = time.time()
    log_request(logger, "POST", "/natural", {"question_length": len(request.question)})
    
    try:
        # Validate input
        is_valid, error_msg = validate_natural_language_question(request.question)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        is_valid, error_msg = validate_max_results(request.max_results)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process query
        processor = get_query_processor()
        result = processor.process_natural_language_query(
            request.question,
            request.max_results
        )
        
        # Convert to response model
        response = NaturalLanguageQueryResponse(**result)
        
        duration = time.time() - start_time
        log_response(logger, 200, duration, response.result_count)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "natural language query")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/spl", response_model=SPLQueryResponse)
async def query_spl(request: SPLQueryRequest):
    """
    Execute raw SPL query directly.
    
    This endpoint executes a raw SPL query against Splunk without any
    natural language processing.
    """
    start_time = time.time()
    log_request(logger, "POST", "/spl", {"query_length": len(request.spl_query)})
    
    try:
        # Validate input
        is_valid, error_msg = validate_spl_query(request.spl_query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        is_valid, error_msg = validate_max_results(request.max_results)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Execute query
        processor = get_query_processor()
        result = processor.execute_spl_query(
            request.spl_query,
            request.max_results
        )
        
        # Convert to response model
        response = SPLQueryResponse(**result)
        
        duration = time.time() - start_time
        log_response(logger, 200, duration, response.result_count)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "SPL query")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/enhance", response_model=QueryEnhancementResponse)
async def enhance_query(request: QueryEnhancementRequest):
    """
    Enhance existing SPL query based on feedback.
    
    This endpoint takes an existing SPL query and user feedback to generate
    an improved version of the query.
    """
    start_time = time.time()
    log_request(logger, "POST", "/enhance", {"query_length": len(request.spl_query)})
    
    try:
        # Validate SPL query
        is_valid, error_msg = validate_spl_query(request.spl_query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Enhance query
        processor = get_query_processor()
        result = processor.openai_client.enhance_spl_query(
            request.spl_query,
            request.feedback
        )
        
        # Convert to response model
        response = QueryEnhancementResponse(**result)
        
        duration = time.time() - start_time
        log_response(logger, 200, duration)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "query enhancement")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/suggestions", response_model=QuerySuggestionResponse)
async def get_suggestions(request: QuerySuggestionRequest):
    """
    Get query suggestions based on partial input.
    
    This endpoint provides suggested completions for natural language questions
    based on partial input.
    """
    start_time = time.time()
    log_request(logger, "POST", "/suggestions", {"partial_length": len(request.partial_question)})
    
    try:
        # Get suggestions
        processor = get_query_processor()
        suggestions = processor.get_query_suggestions(request.partial_question)
        
        # Limit to requested number
        suggestions = suggestions[:request.max_suggestions]
        
        response = QuerySuggestionResponse(
            suggestions=suggestions,
            partial_question=request.partial_question
        )
        
        duration = time.time() - start_time
        log_response(logger, 200, duration, len(suggestions))
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "query suggestions")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of all system components including
    Splunk and OpenAI connectivity.
    """
    start_time = time.time()
    log_request(logger, "GET", "/health")
    
    try:
        processor = get_query_processor()
        health_data = processor.get_health_status()
        
        # Determine HTTP status code based on health
        status_code = 200 if health_data["overall_status"] == "healthy" else 503
        
        response = HealthResponse(
            status=health_data["overall_status"],
            timestamp=health_data["timestamp"],
            services=health_data
        )
        
        duration = time.time() - start_time
        log_response(logger, status_code, duration)
        
        return JSONResponse(
            status_code=status_code,
            content=response.dict()
        )
        
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "health check")
        log_response(logger, 500, duration)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "timestamp": time.time(),
                "error": str(e)
            }
        )

@router.get("/indexes")
async def get_indexes():
    """
    Get available Splunk indexes.
    
    Returns a list of indexes available in the connected Splunk instance.
    """
    start_time = time.time()
    log_request(logger, "GET", "/indexes")
    
    try:
        processor = get_query_processor()
        indexes = processor.splunk_client.get_indexes()
        
        duration = time.time() - start_time
        log_response(logger, 200, duration, len(indexes))
        
        return {
            "success": True,
            "indexes": indexes,
            "count": len(indexes)
        }
        
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "get indexes")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve indexes: {str(e)}"
        )

@router.get("/history")
async def get_search_history(count: int = 10):
    """
    Get recent search history.
    
    Returns a list of recent search queries and their results.
    """
    start_time = time.time()
    log_request(logger, "GET", "/history", {"count": count})
    
    try:
        if count < 1 or count > 100:
            raise HTTPException(status_code=400, detail="Count must be between 1 and 100")
        
        processor = get_query_processor()
        history = processor.splunk_client.get_search_history(count)
        
        duration = time.time() - start_time
        log_response(logger, 200, duration, len(history))
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        log_error(logger, e, "get search history")
        log_response(logger, 500, duration)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve search history: {str(e)}"
        )
