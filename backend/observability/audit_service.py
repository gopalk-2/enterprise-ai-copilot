from .logger import logger
import time


def log_query(user, query):
    logger.info(f"USER={user} QUERY={query}")


def log_response(user, response):
    logger.info(f"USER={user} RESPONSE={response[:200]}")


def log_error(user, error):
    logger.error(f"USER={user} ERROR={error}")


def measure_time(start_time):
    duration = time.time() - start_time
    logger.info(f"RESPONSE_TIME={duration:.2f}s")