from datetime import datetime

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


def parse_query_datetime(value: str, *, end_of_day: bool = False) -> datetime | None:
    """严格解析查询参数中的时间边界：空值返回 None，无法解析时抛 ValueError。

    纯日期（YYYY-MM-DD）按整天处理：end_of_day=True 时取当天 23:59:59.999999，
    避免把 ``to`` 截到当天 00:00 导致窗内行丢失。
    """
    value = (value or "").strip()
    if not value:
        return None
    if len(value) == 10:
        d = datetime.strptime(value, "%Y-%m-%d")
        if end_of_day:
            d = d.replace(hour=23, minute=59, second=59, microsecond=999999)
        return d
    # datetime-local 控件可提交精度只到分钟的值 (YYYY-MM-DDTHH:MM)
    if len(value) == 16:
        value = f"{value}:00"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"无法解析时间: {value}") from exc
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt
