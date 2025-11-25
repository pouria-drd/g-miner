import os
import logging

os.makedirs("logs", exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] | [%(name)s] | [%(levelname)s] | [%(message)s]",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/application.log"),  # Log to a file
        logging.StreamHandler(),  # Log to the console
    ],
)
