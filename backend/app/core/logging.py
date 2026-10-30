import logging
import sys
import re

SENSITIVE_PATTERNS = [
    r'(sk-[a-zA-Z0-9_\-]{20,})',
    r'(AIza[0-9A-Za-z-_]{35})',
    r'(tvly-[a-zA-Z0-9_\-]{20,})',
    r'(password=)[^\s&]+',
]

class SensitiveFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in SENSITIVE_PATTERNS:
                record.msg = re.sub(pattern, "[REDACTED]", record.msg)
        return True

def setup_logging():
    logger = logging.getLogger("mmchatbot")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveFilter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logging()
