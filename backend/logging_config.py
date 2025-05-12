import os
import logging

LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
LOG_FILE = os.path.join(LOG_DIR, "meshspy.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("meshspy")
