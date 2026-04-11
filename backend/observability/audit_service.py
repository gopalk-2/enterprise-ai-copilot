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


# ── Semantic Cache Observability ─────────────────────────────────────────────

def log_cache_hit(user, query):
    logger.info(f"USER={user} CACHE=HIT QUERY={query[:100]}")


def log_cache_miss(user, query):
    logger.info(f"USER={user} CACHE=MISS QUERY={query[:100]}")


def log_redis_error(error):
    logger.warning(f"REDIS_ERROR={error}")