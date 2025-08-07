"""Tests for Splunk client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.splunk_client import SplunkClient

class TestSplunkClient:
    """Test cases for SplunkClient."""
    
    @patch('src.core.splunk_client.client.connect')
    def test_connection_with_token(self, mock_connect):
        """Test connection using token authentication."""
        mock_service = Mock()
        mock_connect.return_value = mock_service
        
        with patch('config.config.config.SPLUNK_TOKEN', 'test-token'):
            splunk_client = SplunkClient()
            
        mock_connect.assert_called_once()
        args, kwargs = mock_connect.call_args
        assert 'splunkToken' in kwargs
        assert kwargs['splunkToken'] == 'test-token'
    
    @patch('src.core.splunk_client.client.connect')
    def test_connection_with_credentials(self, mock_connect):
        """Test connection using username/password."""
        mock_service = Mock()
        mock_connect.return_value = mock_service
        
        with patch('config.config.config.SPLUNK_TOKEN', None):
            with patch('config.config.config.SPLUNK_USERNAME', 'admin'):
                with patch('config.config.config.SPLUNK_PASSWORD', 'password'):
                    splunk_client = SplunkClient()
        
        mock_connect.assert_called_once()
        args, kwargs = mock_connect.call_args
        assert 'username' in kwargs
        assert 'password' in kwargs
    
    def test_execute_search_success(self):
        """Test successful search execution."""
        # Mock setup
        mock_job = Mock()
        mock_job.is_done.return_value = True
        mock_job.__getitem__.side_effect = lambda key: {
            'resultCount': '10',
            'scanCount': '100',
            'runDuration': '1.5'
        }.get(key, '0')
        mock_job.sid = 'test-search-id'
        
        mock_results = [{'field1': 'value1'}, {'field1': 'value2'}]
        
        with patch.object(SplunkClient, '_connect'), \
             patch.object(SplunkClient, 'service') as mock_service:
            
            mock_service.jobs.create.return_value = mock_job
            mock_job.results.return_value = iter([{'field1': 'value1'}, {'field1': 'value2'}])
            
            splunk_client = SplunkClient()
            result = splunk_client.execute_search('search index=main')
            
            assert result['success'] is True
            assert 'results' in result
            assert 'statistics' in result
