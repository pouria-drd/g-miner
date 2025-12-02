from datetime import time


def parse_env_time(env_value: str, default: time) -> time:
    """Convert 'HH:MM' string to datetime.time. Fallback to default if invalid."""
    try:
        hours, minutes = map(int, env_value.split(":"))
        return time(hours, minutes)
    except Exception:
        return default
