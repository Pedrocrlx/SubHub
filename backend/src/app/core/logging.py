"""
Logging configuration for SubHub API

This module provides a complete logging setup with:
- CSV-formatted logs for easy analysis
- Both file and console output
- Timestamp splitting for better data processing
- Automatic log directory creation
"""
import os
import time
import logging
from pathlib import Path
import sys
from datetime import datetime

class CSVLogFormatter(logging.Formatter):
    """
    Custom formatter that creates CSV-structured log entries
    
    Features:
    - Splits timestamps into separate date and time columns
    - Properly escapes message content for CSV compatibility
    - Adds application name for multi-application environments
    """
    
    def format(self, record):
        # Format timestamp according to specified date format
        timestamp = self.formatTime(record, self.datefmt)
        
        # Split timestamp into date and time components
        timestamp_parts = timestamp.split()
        
        try:
            # Normal case - timestamp format is "YYYY-MM-DD HH:MM:SS"
            if len(timestamp_parts) == 2:
                log_date = timestamp_parts[0]  # YYYY-MM-DD
                log_time = timestamp_parts[1]  # HH:MM:SS
            else:
                # Fall back to current time if format is unexpected
                current_time = datetime.now()
                log_date = current_time.strftime("%Y-%m-%d")
                log_time = current_time.strftime("%H:%M:%S")
                
        except Exception as e:
            # Ultimate fallback with clear error indicators
            log_date = "ERROR_DATE"
            log_time = "ERROR_TIME"
            print(f"ERROR: Timestamp formatting failed: {e}", file=sys.stderr)
        
        # Escape message content for CSV compatibility
        message = record.getMessage().replace('"', '""')
            
        # Return properly formatted CSV log entry
        return f'{log_date},{log_time},{record.levelname},{record.name},"{message}"'

def setup_logging(log_level=logging.INFO):
    """
    Configure application logging with both file and console output
    
    Args:
        log_level: The minimum logging level to capture (default: INFO)
        
    Returns:
        tuple: (logger instance, path to the log file)
    """
    # Define logs directory using pathlib for better path handling
    base_dir = Path(__file__).parent.parent.parent
    logs_directory = base_dir / "logs"
    
    # Create logs directory if it doesn't exist
    logs_directory.mkdir(exist_ok=True, parents=True)
    
    # Create uniquely named log file with timestamp and date for readability
    current_date = datetime.now().strftime("%Y%m%d")
    timestamp = int(time.time())
    log_filename = f"subhub_{current_date}_{timestamp}.log"
    log_file_path = logs_directory / log_filename
    
    # Write CSV header as first line of log file
    with open(log_file_path, 'w') as log_file:
        log_file.write('date,time,level,component,message\n')
    
    # Configure root logger with appropriate logging level
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers (important for module reloads)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create file handler for persistent logs
    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(log_level)
    
    # Create console handler for development visibility
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Apply custom CSV formatter to both handlers
    csv_formatter = CSVLogFormatter(datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(csv_formatter)
    console_handler.setFormatter(csv_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create application-specific logger
    app_logger = logging.getLogger("subhub")
    app_logger.info(f"SubHub application started (log file: {log_file_path})")
    
    return app_logger, log_file_path

# Create logger instance for application-wide use
application_logger, log_file_path = setup_logging()