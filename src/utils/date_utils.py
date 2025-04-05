"""Date handling utilities for the Rotterdam Time Machine project.

This module provides utility functions for handling dates in the application.
It includes functions for parsing, formatting, and comparing dates.
"""
from datetime import date, datetime
from typing import Optional

def parse_date(date_str: str) -> Optional[date]:
    """Parse a date string in YYYYMMDD format.
    
    Args:
        date_str: A string representing a date in YYYYMMDD format.
        
    Returns:
        A date object if parsing is successful, None otherwise.
    """
    try:
        return datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        return None

def get_day_month(date_obj: date) -> tuple[int, int]:
    """Extract day and month from a date object.
    
    Args:
        date_obj: A date object to extract day and month from.
        
    Returns:
        A tuple containing (day, month) as integers.
    """
    return date_obj.day, date_obj.month

def find_closest_date(target_date: date, available_dates: list[date]) -> Optional[date]:
    """Find the closest date to the target date from a list of available dates.
    
    Args:
        target_date: The reference date to compare against.
        available_dates: A list of dates to search through.
        
    Returns:
        The date from available_dates that is closest to target_date,
        or None if available_dates is empty.
    """
    if not available_dates:
        return None
    
    # Convert dates to datetime for easier comparison
    target_dt = datetime.combine(target_date, datetime.min.time())
    available_dts = [datetime.combine(d, datetime.min.time()) for d in available_dates]
    
    # Find the closest date
    closest_date = min(available_dts, key=lambda x: abs((x - target_dt).days))
    return closest_date.date() 