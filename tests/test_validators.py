"""
Tests for QueryValidator, SortValidator, and ResultCountValidator
"""

import pytest
from youtube_trending_mcp.validators import (
    QueryValidator,
    SortValidator,
    ResultCountValidator
)


class TestQueryValidator:
    """Test cases for QueryValidator"""
    
    def test_valid_simple_query(self):
        is_valid, error = QueryValidator.validate_query("cute cats")
        assert is_valid is True
        assert error == ""
    
    def test_valid_query_with_spaces(self):
        is_valid, error = QueryValidator.validate_query("cooking recipe tutorial")
        assert is_valid is True
        assert error == ""
    
    def test_valid_query_with_numbers(self):
        is_valid, error = QueryValidator.validate_query("top 10 videos 2024")
        assert is_valid is True
        assert error == ""
    
    def test_empty_query(self):
        is_valid, error = QueryValidator.validate_query("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_whitespace_only_query(self):
        is_valid, error = QueryValidator.validate_query("   ")
        assert is_valid is False
        assert "whitespace" in error.lower()
    
    def test_query_too_long(self):
        long_query = "a" * 201
        is_valid, error = QueryValidator.validate_query(long_query)
        assert is_valid is False
        assert "too long" in error.lower()
    
    def test_query_at_max_length(self):
        max_query = "a" * 200
        is_valid, error = QueryValidator.validate_query(max_query)
        assert is_valid is True
        assert error == ""
    
    def test_forbidden_semicolon(self):
        is_valid, error = QueryValidator.validate_query("query; DROP TABLE")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_forbidden_ampersand(self):
        is_valid, error = QueryValidator.validate_query("query & malicious")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_forbidden_pipe(self):
        is_valid, error = QueryValidator.validate_query("query | another")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_forbidden_dollar(self):
        is_valid, error = QueryValidator.validate_query("query $var")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_forbidden_backtick(self):
        is_valid, error = QueryValidator.validate_query("query`command`")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_forbidden_newline(self):
        is_valid, error = QueryValidator.validate_query("query\nmalicious")
        assert is_valid is False
        assert "forbidden" in error.lower()
    
    def test_suspicious_sql_drop(self):
        is_valid, error = QueryValidator.validate_query("puppies DROP TABLE users")
        assert is_valid is False
        assert "suspicious" in error.lower()
    
    def test_suspicious_sql_union(self):
        is_valid, error = QueryValidator.validate_query("cats UNION SELECT password")
        assert is_valid is False
        assert "suspicious" in error.lower()
    
    def test_non_string_type(self):
        is_valid, error = QueryValidator.validate_query(123)
        assert is_valid is False
        assert "string" in error.lower()
    
    def test_none_query(self):
        is_valid, error = QueryValidator.validate_query(None)
        assert is_valid is False


class TestQueryValidatorSanitize:
    """Test cases for QueryValidator.sanitize_query"""
    
    def test_sanitize_removes_semicolon(self):
        result = QueryValidator.sanitize_query("query; attack")
        assert ";" not in result
    
    def test_sanitize_removes_newline(self):
        result = QueryValidator.sanitize_query("query\nattack")
        assert "\n" not in result
    
    def test_sanitize_truncates_long_query(self):
        long_query = "a" * 300
        result = QueryValidator.sanitize_query(long_query)
        assert len(result) <= 200
    
    def test_sanitize_collapses_spaces(self):
        result = QueryValidator.sanitize_query("multiple    spaces")
        assert "    " not in result


class TestSortValidator:
    """Test cases for SortValidator"""
    
    def test_valid_relevance(self):
        is_valid, error = SortValidator.validate_sort("relevance")
        assert is_valid is True
    
    def test_valid_views(self):
        is_valid, error = SortValidator.validate_sort("views")
        assert is_valid is True
    
    def test_valid_date(self):
        is_valid, error = SortValidator.validate_sort("date")
        assert is_valid is True
    
    def test_invalid_sort_option(self):
        is_valid, error = SortValidator.validate_sort("invalid")
        assert is_valid is False
        assert "relevance" in error
        assert "views" in error
        assert "date" in error
    
    def test_non_string_type(self):
        is_valid, error = SortValidator.validate_sort(123)
        assert is_valid is False
    
    def test_normalize_uppercase(self):
        result = SortValidator.normalize_sort("VIEWS")
        assert result == "views"
    
    def test_normalize_invalid_returns_default(self):
        result = SortValidator.normalize_sort("invalid")
        assert result == "relevance"


class TestResultCountValidator:
    """Test cases for ResultCountValidator"""
    
    def test_valid_count_20(self):
        is_valid, error = ResultCountValidator.validate_max_results(20)
        assert is_valid is True
    
    def test_valid_count_1(self):
        is_valid, error = ResultCountValidator.validate_max_results(1)
        assert is_valid is True
    
    def test_valid_count_100(self):
        is_valid, error = ResultCountValidator.validate_max_results(100)
        assert is_valid is True
    
    def test_count_too_low(self):
        is_valid, error = ResultCountValidator.validate_max_results(0)
        assert is_valid is False
        assert "at least" in error.lower()
    
    def test_count_too_high(self):
        is_valid, error = ResultCountValidator.validate_max_results(101)
        assert is_valid is False
        assert "exceed" in error.lower()
    
    def test_non_int_type(self):
        is_valid, error = ResultCountValidator.validate_max_results("20")
        assert is_valid is False
    
    def test_normalize_low_value(self):
        result = ResultCountValidator.normalize_max_results(-5)
        assert result == 1
    
    def test_normalize_high_value(self):
        result = ResultCountValidator.normalize_max_results(500)
        assert result == 100
    
    def test_normalize_string_to_int(self):
        result = ResultCountValidator.normalize_max_results("50")
        assert result == 50
    
    def test_normalize_invalid_string(self):
        result = ResultCountValidator.normalize_max_results("invalid")
        assert result == 20
