"""Tests for OpenAI client."""

import pytest
from unittest.mock import Mock, patch
from src.core.openai_client import OpenAIClient

class TestOpenAIClient:
    """Test cases for OpenAIClient."""
    
    @patch('src.core.openai_client.OpenAI')
    def test_natural_to_spl_success(self, mock_openai):
        """Test successful natural language to SPL conversion."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "query": "search index=security action=login | stats count by user",
            "explanation": "Search for login events and count by user",
            "confidence": "high"
        }
        '''
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        openai_client = OpenAIClient()
        result = openai_client.natural_to_spl("Show me login events by user")
        
        assert result['success'] is True
        assert 'search index=security' in result['spl_query']
        assert result['confidence'] == 'high'
    
    def test_parse_spl_response_json(self):
        """Test parsing JSON response."""
        openai_client = OpenAIClient()
        
        json_response = '''
        {
            "query": "search index=main | head 10",
            "explanation": "Get first 10 events from main index",
            "confidence": "medium"
        }
        '''
        
        result = openai_client._parse_spl_response(json_response)
        
        assert result['query'] == "search index=main | head 10"
        assert result['confidence'] == "medium"
    
    def test_parse_spl_response_plain_text(self):
        """Test parsing plain text response."""
        openai_client = OpenAIClient()
        
        text_response = "search index=security failed | stats count by src_ip"
        
        result = openai_client._parse_spl_response(text_response)
        
        assert result['query'] == "search index=security failed | stats count by src_ip"
