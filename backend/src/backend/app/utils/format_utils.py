"""
Formatting utility functions for data presentation
"""
from typing import Dict, Any, List
from datetime import date, datetime

def format_currency(amount: float) -> str:
    """Format a numeric value as a currency string"""
    return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """Format a numeric value as a percentage string"""
    return f"{value:.1f}%"

def category_title_case(category: str) -> str:
    """
    Format a category name in title case with consistent spacing
    
    Example:
        "streaming services" -> "Streaming Services"
        "MUSIC apps" -> "Music Apps"
    """
    return " ".join(word.capitalize() for word in category.strip().split())

def format_date(date_obj: date) -> str:
    """Format a date object as a consistent string"""
    return date_obj.strftime("%Y-%m-%d")

def parse_date_string(date_str: str) -> date:
    """Parse a date string into a date object"""
    return date.fromisoformat(date_str)