
"""Unit tests for SplunkClient."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from src.core.splunk_client import SplunkClient
import json

class TestSplunkClient:
    """Test cases for SplunkClient."""

    @patch('src.core.splunk_client.client.connect')
    def test_connect_success(self, mock_connect):
        """Test successful Splunk connection."""
        mock_service = Mock()
        mock_connect.return_value = mock_service

        client_instance = SplunkClient()
        assert client_instance.service == mock_service
        mock_connect.assert_called_once()

    @patch('src.core.splunk_client.client.connect', side_effect=Exception("Connection error"))
    def test_connect_failure(self, mock_connect):
        """Test failure in Splunk connection."""
        with pytest.raises(Exception) as exc_info:
            SplunkClient()
        assert "Connection error" in str(exc_info.value)

    @patch('src.core.splunk_client.SplunkClient._connect')
    def test_execute_search_oneshot_success(self, mock_connect):
        """Test successful oneshot search."""
        mock_service = MagicMock()
        mock_jobs = MagicMock()
        mock_stream = MagicMock()
        # Ensure the mock stream returns a JSON string, as the code expects
        mock_stream.read.return_value = json.dumps({"results": [{"_raw": "event1"}, {"_raw": "event2"}]}).encode('utf-8')
        mock_jobs.oneshot.return_value = mock_stream
        mock_service.jobs = mock_jobs

        client_instance = SplunkClient()
        client_instance.service = mock_service

        result = client_instance.execute_search("error", max_results=10)
        assert result["success"] is True
        assert len(result["results"]) == 2

    #@patch('src.core.splunk_client.SplunkClient._connect')
    #def test_execute_search_job_fallback(self, mock_connect):
    #    """Test fallback to job-based search."""
    #    mock_service = MagicMock()
    #    mock_job = MagicMock()

    #    # Mock oneshot to fail and force the fallback to job-based search
    #    mock_service.jobs.oneshot.side_effect = Exception("Oneshot search failed")

    #    # Set job status flow
    #    mock_job.is_done.side_effect = [False, True]  # simulate wait loop
    #    mock_job.refresh = MagicMock()
    #    mock_job.cancel = MagicMock()
    #
    #    # Correctly patch the job.get method to return expected stats
    #    def job_get(key, default=None):
    #        mapping = {
    #            "resultCount": "5",
    #            "runDuration": "1.5",
    #            "scanCount": "10",
    #        }
    #        return mapping.get(key, default)
    #
    #    mock_job.get.side_effect = job_get
    #    mock_job.sid = "job123"

    #    # Inject the mocked job into the mock service
    #    mock_service.jobs.create.return_value = mock_job
    #    client_instance = SplunkClient()
    #    client_instance.service = mock_service

    #    # The test should call the public execute_search method to trigger the fallback logic
    #    result = client_instance.execute_search("search index=main", max_results=100, timeout=60)

    #    assert result["success"] is True
    #    assert result["statistics"]["search_id"] == "job123"
    #    assert result["statistics"]["result_count"] == 5
    #    assert result["statistics"]["scan_count"] == 10
    #    # The `_execute_job_search` method in splunk_client.py returns an empty list for results
    #    assert result["results"] == []


    @patch('src.core.splunk_client.SplunkClient._connect')
    def test_get_indexes_success(self, mock_connect):
        """Test get_indexes method."""
        mock_service = MagicMock()
        mock_index = MagicMock()
        mock_index.name = "main"
        mock_service.indexes = [mock_index]

        client_instance = SplunkClient()
        client_instance.service = mock_service

        indexes = client_instance.get_indexes()
        assert "main" in indexes

    @patch('src.core.splunk_client.SplunkClient._connect')
    def test_validate_spl_valid(self, mock_connect):
        """Test SPL validation success."""
        mock_service = MagicMock()
        mock_jobs = MagicMock()
        mock_jobs.create.return_value = MagicMock()
        mock_service.jobs = mock_jobs

        client_instance = SplunkClient()
        client_instance.service = mock_service

        result = client_instance.validate_spl("search index=main")
        assert result["valid"] is True

    @patch('src.core.splunk_client.SplunkClient._connect')
    def test_validate_spl_invalid(self, mock_connect):
        """Test SPL validation failure."""
        mock_service = MagicMock()
        mock_jobs = MagicMock()
        mock_jobs.create.side_effect = Exception("Invalid SPL")
        mock_service.jobs = mock_jobs

        client_instance = SplunkClient()
        client_instance.service = mock_service

        result = client_instance.validate_spl("bad query")
        assert result["valid"] is False
        assert "Invalid SPL" in result["error"]

    @patch('src.core.splunk_client.SplunkClient._connect')
    def test_get_search_history_success(self, mock_connect):
        """Test retrieving search history."""
        mock_service = MagicMock()
        mock_job = MagicMock()
        mock_job.sid = "abc123"
        mock_job.content = {
            "search": "search index=main",
            "createTime": "2025-08-01T10:00:00Z",
            "runDuration": "1.23",
            "resultCount": "50"
        }
        mock_service.jobs.list.return_value = [mock_job]

        client_instance = SplunkClient()
        client_instance.service = mock_service

        history = client_instance.get_search_history()
        assert len(history) == 1
        assert history[0]["sid"] == "abc123"
