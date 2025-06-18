import os
import time
import logging
from pathlib import Path
from typing import Tuple, Optional

class TimestampSplitFormatter(logging.Formatter):
    """
    Custom formatter that splits timestamps into separate date and time columns for CSV logs
    
    This allows for easier filtering and analysis in spreadsheet applications.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Format timestamp according to specified date format
        record.asctime = self.formatTime(record, self.datefmt)
        
        try:
            # Split timestamp into date and time components
            timestamp_parts = record.asctime.split()
            if len(timestamp_parts) == 2:
                record.date_part = timestamp_parts[0]  # YYYY-MM-DD
                record.time_part = timestamp_parts[1]  # HH:MM:SS
            else:
                # Handle unexpected format with clear error markers
                record.date_part = "ERROR_DATE"
                record.time_part = "ERROR_TIME"
                print(f"ERROR: Timestamp format error: '[{record.asctime}]'")
        except Exception as e:
            # Fallback if any error occurs during formatting
            record.date_part = "ERROR"
            record.time_part = str(int(time.time()))
            print(f"ERROR: Timestamp formatting exception: [{str(e)}]")
            
        # Return CSV-formatted log entry with quotes around message to handle commas within text
        return f'{record.date_part},{record.time_part},{record.levelname},{record.name},"{record.getMessage()}"'

def setup_logging(log_level: int = logging.INFO) -> Tuple[logging.Logger, Path]:
    """
    Configure application logging with both file and console output
    
    Args:
        log_level: The logging level to use (default: logging.INFO)
        
    Returns:
        Tuple containing the configured logger and the path to the log file
    """
    # Define logs directory relative to application location using pathlib
    logs_directory = Path(__file__).parent.parent.parent / "logs"
    
    # Create logs directory if it doesn't exist
    logs_directory.mkdir(exist_ok=True, parents=True)
    
    # Create uniquely named log file with timestamp
    log_file_path = logs_directory / f"log_{int(time.time())}.log"
    
    try:
        # Write CSV header as first line of log file
        with open(log_file_path, 'w') as log_file:
            log_file.write('date,time,level,name,message\n')
        
        # Configure root logger with file and console output
        logging.basicConfig(
            level=log_level,
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
        application_logger.info(f"SubHub initiated (log file: [{str(log_file_path)}])")
        
        return application_logger, log_file_path
        
    except Exception as e:
        # Fallback to console-only logging if file setup fails
        print(f"WARNING: Failed to set up log file: [{str(e)}]")
        print(f"Falling back to console-only logging")
        
        # Configure console-only logging
        logging.basicConfig(
            level=log_level,
            handlers=[logging.StreamHandler()]
        )
        
        # Apply custom formatter
        console_formatter = TimestampSplitFormatter(datefmt='%Y-%m-%d %H:%M:%S')
        for log_handler in logging.getLogger().handlers:
            log_handler.setFormatter(console_formatter)
            
        # Create application logger
        application_logger = logging.getLogger("log")
        application_logger.warning(f"SubHub initiated with console-only logging due to error: [{str(e)}]")
        
        return application_logger, Path("console_only_no_file")

# Create logger instance
application_logger, log_file_path = setup_logging()