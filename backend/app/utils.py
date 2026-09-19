from datetime import datetime, time

from flask import jsonify


def error(message: str, status: int = 400):
    return jsonify({"message": message}), status


def normalize_datetime(value: str) -> datetime:
    value = (value or "").strip()
    if not value:
        return datetime.now()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value.replace("Z", "")[:26], fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now()


def dt_to_json(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_query_datetime(value: str, end_of_day: bool = False) -> datetime | None:
    """Parse a query-string datetime bound; None when unparseable.

    Keeps the full time component (a ``date`` would silently truncate the
    window). A date-only value covers the whole day: 00:00:00 normally, or
    23:59:59.999999 when ``end_of_day`` is set (inclusive ``to`` bound).
    """
    value = (value or "").strip()
    if not value:
        return None
    candidate = value.replace("Z", "")[:26]
    dt = None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(candidate, fmt)
            break
        except ValueError:
            continue
    if dt is None:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
    if end_of_day and len(value) <= 10:
        dt = datetime.combine(dt.date(), time.max)
    return dt
