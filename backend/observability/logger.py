import logging
import os

# Relative to this file: ../../data/logs  (backend/observability/ → backend/ → project root / data/logs)
_here = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(_here, "..", "..", "data", "logs")

os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, "ai_assistant.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("ai_assistant")