import logging
import sys

# Create a logger
logger = logging.getLogger("misleep_logger")
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('./misleep/logger.log')
file_handler.setLevel(logging.INFO)

# Create a stream handler to print the log in the command line window
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
