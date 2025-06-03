
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Create a logger instance
application_logger = logging.getLogger("subhub")
"""
Logging configuration for SubHub API
"""

class TimestampSplitFormatter(logging.Formatter):
    """Custom formatter that splits timestamps into separate date and time columns for CSV logs"""
    
    def format(self, record):
        # Format timestamp according to specified date format
        record.asctime = self.formatTime(record, self.datefmt)
        
        # Split timestamp into date and time components
        timestamp_parts = record.asctime.split()
        if len(timestamp_parts) == 2:
            record.date_part = timestamp_parts[0]  # YYYY-MM-DD
            record.time_part = timestamp_parts[1]  # HH:MM:SS
        else:
            # Handle unexpected format with clear error markers
            record.date_part = "ERROR_DATE"
            record.time_part = "ERROR_TIME"
            print(f"ERROR: Timestamp format error: '{record.asctime}'")
            
        # Return CSV-formatted log entry
        return f'{record.date_part},{record.time_part},{record.levelname},{record.name},"{record.getMessage()}"'

def setup_logging():
    """Configure application logging with both file and console output"""
    
    # Define logs directory relative to application location
    logs_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)
    
    # Create uniquely named log file with timestamp
    log_file_path = os.path.join(logs_directory, f"log_{int(time.time())}.log")
    
    # Write CSV header as first line of log file
    with open(log_file_path, 'w') as log_file:
        log_file.write('date,time,level,name,message\n')
    
    # Configure root logger with file and console output
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(log_file_path, mode='a'),  # Append to log file
            logging.StreamHandler()  # Output to console
        ]
    )
    
    # Apply custom formatter to all handlers
    csv_formatter = TimestampSplitFormatter(datefmt='%Y-%m-%d %H:%M:%S')
    for log_handler in logging.getLogger().handlers:
        log_handler.setFormatter(csv_formatter)
    
    # Create application logger
    application_logger = logging.getLogger("log")
    application_logger.info(f"SubHub initiated (log file: [{log_file_path}])")
    
    return application_logger, log_file_path

# Create logger instance
application_logger, log_file_path = setup_logging()
