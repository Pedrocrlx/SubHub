"""
Formatting utility functions for data presentation

This module provides consistent formatting functions for:
- Currency values with dollar sign ($)
- Percentage values with percent sign (%)
- Category names with proper capitalization
- Date formatting and parsing using ISO 8601 format (YYYY-MM-DD)
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime

def format_currency(amount: float) -> str:
    """
    Format a numeric value as a currency string with dollar sign
    
    Args:
        amount: Monetary value to format
        
    Returns:
        Formatted string with dollar sign and two decimal places
        
    Examples:
        >>> format_currency(12.5)
        '$12.50'
        >>> format_currency(1234.567)
        '$1234.57'
    """
    return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """
    Format a numeric value as a percentage string
    
    Args:
        value: Percentage value to format (already in percent form, not decimal)
        
    Returns:
        Formatted string with one decimal place and percent sign
        
    Examples:
        >>> format_percentage(75.5)
        '75.5%'
        >>> format_percentage(33.333)
        '33.3%'
    """
    return f"{value:.1f}%"

def category_title_case(category_name: str) -> str:
    """
    Format a category name in title case with consistent spacing
    
    Properly capitalizes each word in a category name and
    ensures consistent spacing.
    
    Args:
        category_name: Raw category name to format
        
    Returns:
        Properly formatted category name
        
    Examples:
        >>> category_title_case("streaming services")
        'Streaming Services'
        >>> category_title_case("MUSIC apps")
        'Music Apps'
        >>> category_title_case("  cloud STORAGE  ")
        'Cloud Storage'
    """
    if not category_name or not isinstance(category_name, str):
        return ""
        
    # Remove extra whitespace and split into words
    words = [word.capitalize() for word in category_name.strip().split()]
    
    # Join words with single spaces
    return " ".join(words)

def format_date(date_value: date) -> str:
    """
    Format a date object as a consistent ISO 8601 string (YYYY-MM-DD)
    
    Args:
        date_value: Date object to format
        
    Returns:
        ISO 8601 formatted date string
        
    Examples:
        >>> format_date(date(2025, 6, 21))
        '2025-06-21'
    """
    return date_value.strftime("%Y-%m-%d")

def parse_date_string(date_string: str) -> Optional[date]:
    """
    Parse a date string into a date object
    
    Expects ISO 8601 format (YYYY-MM-DD)
    
    Args:
        date_string: String representation of a date
        
    Returns:
        Date object if parsing succeeds, None if parsing fails
        
    Examples:
        >>> parse_date_string("2025-06-21")
        datetime.date(2025, 6, 21)
        >>> parse_date_string("invalid")
        None
    """
    try:
        return date.fromisoformat(date_string)
    except (ValueError, TypeError):
        # Return None when string format is invalid
        return None