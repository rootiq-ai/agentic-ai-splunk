"""Query processor that orchestrates OpenAI and Splunk interactions."""

from typing import Dict, Any, Optional, List
import time
from src.core.splunk_client import SplunkClient
from src.core.openai_client import OpenAIClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class QueryProcessor:
    """Main processor for handling natural language to SPL queries."""
    
    def __init__(self):
        """Initialize query processor."""
        self.splunk_client = SplunkClient()
        self.openai_client = OpenAIClient()
        self._cache = {}
        self._context_cache_ttl = 300  # 5 minutes
    
    def process_natural_language_query(self, question: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Process natural language question end-to-end.
        
        Args:
            question: Natural language question
            max_results: Maximum number of results to return
            
        Returns:
            Complete response with SPL, results, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing natural language query: {question}")
            
            # Step 1: Get Splunk context
            context = self._get_splunk_context()
            
            # Step 2: Convert to SPL
            spl_result = self.openai_client.natural_to_spl(question, context)
            
            if not spl_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to convert question to SPL",
                    "details": spl_result,
                    "processing_time": time.time() - start_time
                }
            
            spl_query = spl_result.get("spl_query", "")
            
            if not spl_query:
                return {
                    "success": False,
                    "error": "No valid SPL query generated",
                    "spl_result": spl_result,
                    "processing_time": time.time() - start_time
                }
            
            # Step 3: Validate SPL
            validation = self.splunk_client.validate_spl(spl_query)
            if not validation.get("valid"):
                logger.warning(f"SPL validation failed: {validation.get('error')}")
                # Continue anyway, sometimes validation is overly strict
            
            # Step 4: Execute query
            search_result = self.splunk_client.execute_search(spl_query, max_results)
            
            # Step 5: Compile response
            response = {
                "success": search_result.get("success", False),
                "question": question,
                "spl_query": spl_query,
                "explanation": spl_result.get("explanation", ""),
                "confidence": spl_result.get("confidence", "medium"),
                "results": search_result.get("results", []),
                "result_count": len(search_result.get("results", [])),
                "statistics": search_result.get("statistics", {}),
                "validation": validation,
                "processing_time": time.time() - start_time
            }
            
            if not search_result.get("success"):
                response["error"] = search_result.get("error", "Unknown execution error")
            
            logger.info(f"Query processed in {response['processing_time']:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "processing_time": time.time() - start_time
            }
    
    def execute_spl_query(self, spl_query: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Execute raw SPL query directly.
        
        Args:
            spl_query: SPL query string
            max_results: Maximum number of results to return
            
        Returns:
            Query results and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Executing SPL query: {spl_query}")
            
            # Validate query
            validation = self.splunk_client.validate_spl(spl_query)
            
            # Execute query
            search_result = self.splunk_client.execute_search(spl_query, max_results)
            
            response = {
                "success": search_result.get("success", False),
                "spl_query": spl_query,
                "results": search_result.get("results", []),
                "result_count": len(search_result.get("results", [])),
                "statistics": search_result.get("statistics", {}),
                "validation": validation,
                "processing_time": time.time() - start_time
            }
            
            if not search_result.get("success"):
                response["error"] = search_result.get("error", "Unknown execution error")
            
            return response
            
        except Exception as e:
            logger.error(f"SPL execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "spl_query": spl_query,
                "processing_time": time.time() - start_time
            }
    
    def get_query_suggestions(self, partial_question: str) -> List[str]:
        """
        Get query suggestions based on partial input.
        
        Args:
            partial_question: Partial question text
            
        Returns:
            List of suggested completions
        """
        suggestions = [
            "Show me error logs from the last hour",
            "What are the top source IPs by traffic volume?",
            "Find failed login attempts in the last 24 hours",
            "Show me the most common HTTP status codes",
            "Which users have logged in today?",
            "What are the top 10 processes by CPU usage?",
            "Show me security events from the last week",
            "Find all 404 errors in web logs",
            "What hosts are generating the most events?",
            "Show me database connection errors"
        ]
        
        # Simple matching - in production, use more sophisticated NLP
        partial_lower = partial_question.lower()
        filtered_suggestions = [
            s for s in suggestions 
            if any(word in s.lower() for word in partial_lower.split())
        ]
        
        return filtered_suggestions[:5]  # Return top 5 matches
    
    def _get_splunk_context(self) -> Dict[str, Any]:
        """Get Splunk environment context for better SPL generation."""
        cache_key = "splunk_context"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if time.time() - cached_time < self._context_cache_ttl:
                return cached_data
        
        try:
            context = {
                "indexes": self.splunk_client.get_indexes(),
                "common_fields": [
                    "host", "source", "sourcetype", "_time", "index",
                    "user", "action", "status", "method", "uri_path",
                    "src_ip", "dest_ip", "bytes", "duration"
                ]
            }
            
            # Cache the context
            self._cache[cache_key] = (time.time(), context)
            
            return context
            
        except Exception as e:
            logger.warning(f"Failed to get Splunk context: {str(e)}")
            return {
                "indexes": ["main", "_internal"],
                "common_fields": ["host", "source", "sourcetype", "_time"]
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all components."""
        health = {
            "timestamp": time.time(),
            "overall_status": "healthy"
        }
        
        # Check Splunk connection
        try:
            indexes = self.splunk_client.get_indexes()
            health["splunk"] = {
                "status": "connected",
                "indexes_count": len(indexes)
            }
        except Exception as e:
            health["splunk"] = {
                "status": "error",
                "error": str(e)
            }
            health["overall_status"] = "degraded"
        
        # Check OpenAI (simple check)
        try:
            # Just verify the client is initialized with a key
            if self.openai_client.client.api_key:
                health["openai"] = {"status": "configured"}
            else:
                health["openai"] = {"status": "not_configured"}
                health["overall_status"] = "degraded"
        except Exception as e:
            health["openai"] = {
                "status": "error",
                "error": str(e)
            }
            health["overall_status"] = "degraded"
        
        return health
