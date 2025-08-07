"""OpenAI client for natural language to SPL conversion."""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIClient:
    """Client for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def natural_to_spl(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert natural language question to SPL query.
        
        Args:
            question: Natural language question
            context: Optional context (indexes, sourcetypes, etc.)
            
        Returns:
            Dictionary containing SPL query and metadata
        """
        try:
            logger.info(f"Converting natural language to SPL: {question}")
            
            # Build system prompt with SPL knowledge
            system_prompt = self._build_system_prompt(context)
            
            # User message
            user_message = f"Convert this question to SPL: {question}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response
            content = response.choices[0].message.content
            spl_info = self._parse_spl_response(content)
            
            logger.info(f"Generated SPL: {spl_info.get('query', '')}")
            
            return {
                "success": True,
                "spl_query": spl_info.get("query", ""),
                "explanation": spl_info.get("explanation", ""),
                "confidence": spl_info.get("confidence", "medium"),
                "original_question": question
            }
            
        except Exception as e:
            logger.error(f"Failed to convert natural language to SPL: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_question": question
            }
    
    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt for SPL conversion."""
        base_prompt = """You are an expert Splunk SPL (Search Processing Language) query generator. Your task is to convert natural language questions into accurate SPL queries.

SPL Syntax Guidelines:
- Always start with 'search' command
- Use pipe (|) to chain commands
- Common commands: search, stats, eval, where, sort, head, tail, table, fields
- Time ranges: earliest=-1h, latest=now, etc.
- Field operations: field=value, field!="value", field>10
- Statistics: count, sum, avg, max, min, dc (distinct count)
- Grouping: by field_name

Common Patterns:
- Error logs: search index=* error OR failed | head 100
- Login events: search index=security action=login | stats count by user
- Time-based: search index=* earliest=-24h latest=now
- Top values: search index=* | top 10 field_name
- Failed attempts: search index=* (failed OR error) | stats count by host

Response Format:
Provide your response as JSON with these fields:
{
    "query": "the SPL query",
    "explanation": "brief explanation of what the query does",
    "confidence": "high|medium|low"
}

"""
        
        if context:
            if context.get("indexes"):
                base_prompt += f"\nAvailable indexes: {', '.join(context['indexes'])}\n"
            if context.get("common_fields"):
                base_prompt += f"\nCommon fields: {', '.join(context['common_fields'])}\n"
        
        return base_prompt
    
    def _parse_spl_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response to extract SPL query."""
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)
            
            # If not JSON, look for query patterns
            lines = content.split('\n')
            query = ""
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('search '):
                    query = line
                elif 'explanation' in line.lower() or 'does' in line.lower():
                    explanation = line
            
            return {
                "query": query,
                "explanation": explanation,
                "confidence": "medium"
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse SPL response: {str(e)}")
            # Fallback: treat entire content as query if it starts with 'search'
            if content.strip().startswith('search '):
                return {
                    "query": content.strip(),
                    "explanation": "Query generated from natural language",
                    "confidence": "low"
                }
            
            return {
                "query": "",
                "explanation": "Failed to parse response",
                "confidence": "low"
            }
    
    def enhance_spl_query(self, spl_query: str, feedback: str) -> Dict[str, Any]:
        """
        Enhance existing SPL query based on feedback.
        
        Args:
            spl_query: Existing SPL query
            feedback: User feedback or requirements
            
        Returns:
            Dictionary containing enhanced SPL query
        """
        try:
            system_prompt = """You are an expert at improving SPL queries. Given an existing SPL query and user feedback, provide an improved version.

Focus on:
- Performance optimization
- Better field selection
- More specific filtering
- Proper time ranges
- Statistical accuracy

Respond with JSON format:
{
    "query": "improved SPL query",
    "changes": "description of changes made",
    "confidence": "high|medium|low"
}"""
            
            user_message = f"Original query: {spl_query}\nFeedback: {feedback}\nProvide an improved query."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            enhanced_info = json.loads(content)
            
            return {
                "success": True,
                "enhanced_query": enhanced_info.get("query", spl_query),
                "changes": enhanced_info.get("changes", ""),
                "confidence": enhanced_info.get("confidence", "medium"),
                "original_query": spl_query
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance SPL query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_query": spl_query
            }
