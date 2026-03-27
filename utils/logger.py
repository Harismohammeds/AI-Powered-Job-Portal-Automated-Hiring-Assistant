import logging
import os

# create logs folder
os.makedirs("logs", exist_ok=True)

# create file path
log_file = os.path.join("logs", "app.log")

# create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create file handler
file_handler = logging.FileHandler(log_file)

# format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# add handler
logger.addHandler(file_handler)