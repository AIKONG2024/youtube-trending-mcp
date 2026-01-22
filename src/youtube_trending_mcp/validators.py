"""
Query validation for user input

Security-focused validation for LLM-driven queries.
Based on MCP best practices and Pydantic-style validation.
"""

from typing import Tuple, List
import re


class QueryValidator:
    """
    Validate user-provided search queries
    
    Security measures:
    - Length limits (1-200 chars)
    - Forbidden character filtering
    - Empty/whitespace-only rejection
    - SQL injection pattern detection
    """
    
    MAX_QUERY_LENGTH = 200
    MIN_QUERY_LENGTH = 1
    
    # Characters that could be used for injection attacks
    FORBIDDEN_CHARS = [';', '&', '|', '$', '`', '\n', '\r', '\t', '<', '>']
    
    # Patterns that might indicate injection attempts
    SUSPICIOUS_PATTERNS = [
        r'--',           # SQL comment
        r'/\*',          # SQL block comment start
        r'\*/',          # SQL block comment end
        r'(?i)drop\s+table',   # SQL DROP TABLE
        r'(?i)delete\s+from',  # SQL DELETE
        r'(?i)insert\s+into',  # SQL INSERT
        r'(?i)union\s+select', # SQL UNION injection
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, str]:
        """
        Validate search query
        
        Args:
            query: User-provided search query
        
        Returns:
            Tuple of (is_valid, error_message)
            - If valid: (True, "")
            - If invalid: (False, "descriptive error message")
        
        Examples:
            >>> QueryValidator.validate_query("cute cats")
            (True, "")
            
            >>> QueryValidator.validate_query("")
            (False, "Query cannot be empty")
            
            >>> QueryValidator.validate_query("query; DROP TABLE")
            (False, "Forbidden character: ';'")
        """
        # Type check
        if not isinstance(query, str):
            return False, f"Query must be a string, got {type(query).__name__}"
        
        # Empty check
        if not query:
            return False, "Query cannot be empty"
        
        # Whitespace-only check
        stripped = query.strip()
        if not stripped:
            return False, "Query cannot be only whitespace"
        
        # Length check - too short
        if len(stripped) < cls.MIN_QUERY_LENGTH:
            return False, f"Query too short (min {cls.MIN_QUERY_LENGTH} character)"
        
        # Length check - too long
        if len(query) > cls.MAX_QUERY_LENGTH:
            return False, f"Query too long (max {cls.MAX_QUERY_LENGTH} characters, got {len(query)})"
        
        # Forbidden characters check
        for char in cls.FORBIDDEN_CHARS:
            if char in query:
                char_repr = repr(char)
                return False, f"Forbidden character: {char_repr}"
        
        # Suspicious patterns check
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query):
                return False, "Query contains suspicious pattern"
        
        return True, ""
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """
        Sanitize query by removing forbidden characters
        
        Note: This is a fallback method. Prefer validate_query() 
        and reject invalid queries rather than silently sanitizing.
        
        Args:
            query: User-provided search query
        
        Returns:
            Sanitized query string
        """
        if not isinstance(query, str):
            return ""
        
        result = query
        
        # Remove forbidden characters
        for char in cls.FORBIDDEN_CHARS:
            result = result.replace(char, ' ')
        
        # Collapse multiple spaces
        result = ' '.join(result.split())
        
        # Truncate if too long
        if len(result) > cls.MAX_QUERY_LENGTH:
            result = result[:cls.MAX_QUERY_LENGTH]
        
        return result.strip()
    
    @classmethod
    def get_validation_rules(cls) -> dict:
        """
        Get validation rules for documentation/API schema
        
        Returns:
            Dictionary describing validation rules
        """
        return {
            "min_length": cls.MIN_QUERY_LENGTH,
            "max_length": cls.MAX_QUERY_LENGTH,
            "forbidden_chars": cls.FORBIDDEN_CHARS,
            "description": "Search query must be 1-200 characters, no special characters"
        }


class SortValidator:
    """Validate sort options"""
    
    VALID_SORT_OPTIONS = ["relevance", "views", "date"]
    
    @classmethod
    def validate_sort(cls, sort_by: str) -> Tuple[bool, str]:
        """
        Validate sort option
        
        Args:
            sort_by: Sort option string
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(sort_by, str):
            return False, f"sort_by must be a string, got {type(sort_by).__name__}"
        
        if sort_by.lower() not in cls.VALID_SORT_OPTIONS:
            valid_options = ', '.join(cls.VALID_SORT_OPTIONS)
            return False, f"Invalid sort option: '{sort_by}'. Valid options: {valid_options}"
        
        return True, ""
    
    @classmethod
    def normalize_sort(cls, sort_by: str) -> str:
        """
        Normalize sort option to lowercase
        
        Args:
            sort_by: Sort option string
        
        Returns:
            Normalized sort option or default
        """
        if not isinstance(sort_by, str):
            return "relevance"
        
        normalized = sort_by.lower().strip()
        if normalized in cls.VALID_SORT_OPTIONS:
            return normalized
        
        return "relevance"


class ResultCountValidator:
    """Validate result count parameters"""
    
    MIN_RESULTS = 1
    MAX_RESULTS = 100
    DEFAULT_RESULTS = 20
    
    @classmethod
    def validate_max_results(cls, max_results: int) -> Tuple[bool, str]:
        """
        Validate max_results parameter
        
        Args:
            max_results: Maximum results to return
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(max_results, int):
            return False, f"max_results must be an integer, got {type(max_results).__name__}"
        
        if max_results < cls.MIN_RESULTS:
            return False, f"max_results must be at least {cls.MIN_RESULTS}"
        
        if max_results > cls.MAX_RESULTS:
            return False, f"max_results cannot exceed {cls.MAX_RESULTS}"
        
        return True, ""
    
    @classmethod
    def normalize_max_results(cls, max_results) -> int:
        """
        Normalize max_results to valid range
        
        Args:
            max_results: Maximum results value
        
        Returns:
            Normalized integer within valid range
        """
        try:
            value = int(max_results)
        except (ValueError, TypeError):
            return cls.DEFAULT_RESULTS
        
        if value < cls.MIN_RESULTS:
            return cls.MIN_RESULTS
        if value > cls.MAX_RESULTS:
            return cls.MAX_RESULTS
        
        return value
