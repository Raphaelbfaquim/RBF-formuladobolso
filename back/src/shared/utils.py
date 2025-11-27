from datetime import datetime
from typing import Optional
import pytz


def get_utc_now() -> datetime:
    """Retorna datetime atual em UTC"""
    return datetime.now(pytz.UTC)


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """Converte string de data para datetime"""
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

