"""Input validation utilities."""

import re
from typing import Dict, Any, List, Tuple, Optional

class ValidationError(Exception):
    """Custom validation error."""
    pass

def validate_natural_language_question(question: str) -> Tuple[bool, Optional[str]]:
    """
    Validate natural language question input.
    
    Args:
        question: The question to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "Question cannot be empty"
    
    if len(question.strip()) < 5:
        return False, "Question must be at least 5 characters long"
    
    if len(question) > 1000:
        return False, "Question must be less than 1000 characters"
    
    # Check for potentially malicious content
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'eval\s*\(',
        r'exec\s*\(',
        r'system\s*\(',
        r'__import__',
        r'subprocess'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return False, "Question contains potentially unsafe content"
    
    return True, None

def validate_spl_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate SPL query for basic safety and syntax.
    
    Args:
        query: SPL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "SPL query cannot be empty"
    
    query = query.strip()
    
    # Must start with 'search' command (basic SPL requirement)
    if not query.lower().startswith('search'):
        return False, "SPL query must start with 'search' command"
    
    # Check query length
    if len(query) > 5000:
        return False, "SPL query too long (max 5000 characters)"
    
    # Check for potentially dangerous commands
    dangerous_commands = [
        'delete',
        'drop',
        'truncate',
        'alter',
        'create',
        'update',
        'insert',
        'outputcsv',
        'outputlookup',
        'script',
        'sendemail'
    ]
    
    query_lower = query.lower()
    for cmd in dangerous_commands:
        if re.search(r'\b' + cmd + r'\b', query_lower):
            return False, f"SPL query contains potentially dangerous command: {cmd}"
    
    # Check for balanced pipes (basic syntax check)
    pipe_pattern = r'\|'
    pipes = re.findall(pipe_pattern, query)
    
    # Basic validation - should not have pipes at the beginning or multiple consecutive pipes
    if re.search(r'^\s*\|', query) or re.search(r'\|\s*\|', query):
        return False, "Invalid pipe usage in SPL query"
    
    return True, None

def validate_max_results(max_results: int) -> Tuple[bool, Optional[str]]:
    """
    Validate max_results parameter.
    
    Args:
        max_results: Maximum number of results to return
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(max_results, int):
        return False, "max_results must be an integer"
    
    if max_results < 1:
        return False, "max_results must be greater than 0"
    
    if max_results > 10000:
        return False, "max_results cannot exceed 10,000"
    
    return True, None

def sanitize_input(input_str: str) -> str:
    """
    Sanitize input string by removing potentially harmful characters.
    
    Args:
        input_str: String to sanitize
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove null bytes and other control characters
    sanitized = input_str.replace('\x00', '')
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def validate_request_size(data: Dict[str, Any], max_size_mb: float = 1.0) -> Tuple[bool, Optional[str]]:
    """
    Validate request data size.
    
    Args:
        data: Request data to validate
        max_size_mb: Maximum size in MB
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import sys
    
    try:
        size_bytes = sys.getsizeof(str(data))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return False, f"Request too large: {size_mb:.2f}MB (max: {max_size_mb}MB)"
        
        return True, None
        
    except Exception as e:
        return False, f"Failed to validate request size: {str(e)}"

def validate_field_names(fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate Splunk field names.
    
    Args:
        fields: List of field names to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not fields:
        return True, None
    
    # Splunk field name pattern: alphanumeric, underscore, dash, dot
    field_pattern = re.compile(r'^[a-zA-Z0-9_.\-]+$')
    
    for field in fields:
        if not field or not field.strip():
            return False, "Field name cannot be empty"
        
        if len(field) > 255:
            return False, f"Field name too long: {field[:50]}..."
        
        if not field_pattern.match(field):
            return False, f"Invalid field name: {field[:50]}"
    
    return True, None

def validate_time_range(earliest: str = None, latest: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Splunk time range parameters.
    
    Args:
        earliest: Earliest time (Splunk format)
        latest: Latest time (Splunk format)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Common Splunk time formats
    time_patterns = [
        r'^-?\d+[smhdMy]$',  # Relative time: -1h, -30m, etc.
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',  # ISO format
        r'^now$',  # Special keyword
        r'^@[a-z]+$',  # Snap times: @h, @d, etc.
        r'^\d{10}(\.\d{3})?$'  # Unix timestamp
    ]
    
    for time_param, time_value in [('earliest', earliest), ('latest', latest)]:
        if time_value is None:
            continue
        
        # Check if any pattern matches
        valid = any(re.match(pattern, time_value) for pattern in time_patterns)
        
        if not valid:
            return False, f"Invalid {time_param} time format: {time_value}"
    
    return True, None
