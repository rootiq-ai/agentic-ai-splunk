"""Splunk client for executing SPL queries."""

import json
import time
from typing import Dict, List, Any, Optional
import splunklib.client as client
import splunklib.results as results
from config.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SplunkClient:
    """Client for interacting with Splunk."""
    
    def __init__(self):
        """Initialize Splunk client."""
        self.service = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Splunk service."""
        try:
            connection_params = {
                "host": config.SPLUNK_HOST,
                "port": config.SPLUNK_PORT,
                "scheme": config.SPLUNK_SCHEME
            }
            
            # Use token authentication if available
            if config.SPLUNK_TOKEN:
                connection_params["splunkToken"] = config.SPLUNK_TOKEN
            else:
                connection_params.update({
                    "username": config.SPLUNK_USERNAME,
                    "password": config.SPLUNK_PASSWORD
                })
            
            self.service = client.connect(**connection_params)
            logger.info("Successfully connected to Splunk")
            
        except Exception as e:
            logger.error(f"Failed to connect to Splunk: {str(e)}")
            raise
    
    def execute_search(self, spl_query: str, max_results: int = 100, timeout: int = 60) -> Dict[str, Any]:
        """
        Execute SPL search query.
        
        Args:
            spl_query: The SPL query to execute
            max_results: Maximum number of results to return
            timeout: Query timeout in seconds
            
        Returns:
            Dictionary containing search results and metadata
        """
        if not self.service:
            self._connect()
        
        try:
            logger.info(f"Executing SPL query: {spl_query}")
            
            # Create search job
            search_kwargs = {
                "count": max_results,
                "output_mode": "json"
            }
            
            job = self.service.jobs.create(spl_query, **search_kwargs)
            
            # Wait for job completion
            start_time = time.time()
            while not job.is_done():
                if time.time() - start_time > timeout:
                    job.cancel()
                    raise TimeoutError(f"Search timed out after {timeout} seconds")
                time.sleep(1)
                job.refresh()
            
            # Get results
            result_count = int(job["resultCount"])
            results_reader = results.ResultsReader(job.results())
            
            search_results = []
            for result in results_reader:
                if isinstance(result, dict):
                    search_results.append(result)
            
            # Get job statistics
            stats = {
                "result_count": result_count,
                "scan_count": int(job.get("scanCount", 0)),
                "run_duration": float(job.get("runDuration", 0)),
                "is_done": job.is_done(),
                "search_id": job.sid
            }
            
            logger.info(f"Search completed. Results: {result_count}, Duration: {stats['run_duration']}s")
            
            return {
                "success": True,
                "results": search_results,
                "statistics": stats,
                "query": spl_query
            }
            
        except Exception as e:
            logger.error(f"Search execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": spl_query
            }
    
    def get_indexes(self) -> List[str]:
        """Get list of available indexes."""
        try:
            if not self.service:
                self._connect()
            
            indexes = []
            for index in self.service.indexes:
                indexes.append(index.name)
            
            return indexes
            
        except Exception as e:
            logger.error(f"Failed to get indexes: {str(e)}")
            return []
    
    def validate_spl(self, spl_query: str) -> Dict[str, Any]:
        """
        Validate SPL query syntax.
        
        Args:
            spl_query: The SPL query to validate
            
        Returns:
            Dictionary containing validation results
        """
        try:
            if not self.service:
                self._connect()
            
            # Create a parse-only job to validate syntax
            job = self.service.jobs.create(
                spl_query,
                parse_only=True
            )
            
            return {
                "valid": True,
                "query": spl_query
            }
            
        except Exception as e:
            logger.warning(f"SPL validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "query": spl_query
            }
    
    def get_search_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history."""
        try:
            if not self.service:
                self._connect()
            
            jobs = []
            for job in self.service.jobs.list(count=count):
                jobs.append({
                    "sid": job.sid,
                    "search": job.content.get("search", ""),
                    "create_time": job.content.get("createTime", ""),
                    "run_duration": job.content.get("runDuration", 0),
                    "result_count": job.content.get("resultCount", 0)
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get search history: {str(e)}")
            return []
