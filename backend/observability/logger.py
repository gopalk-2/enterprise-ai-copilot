import logging
import os

LOG_PATH = "/Users/gopalkumar/Desktop/enterprise-ai-assistant/data/logs"

os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_PATH}/ai_assistant.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("ai_assistant")