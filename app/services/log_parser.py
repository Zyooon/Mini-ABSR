import csv
import io
import logging
from datetime import datetime

log = logging.getLogger(__name__)

REQUIRED_FIELDS = {"timestamp", "device_type", "src_ip", "dst_ip", "event_type"}

TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
]


def parse_csv_bytes(content: bytes) -> list[dict]:
    """CSV 파일 바이트를 읽어 행 목록으로 변환한다."""
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def validate_log_row(row: dict) -> tuple[bool, str]:
    """필수 필드 존재 및 값 공백 여부를 검증한다.

    Returns:
        (유효 여부, 오류 메시지)
    """
    missing_fields = REQUIRED_FIELDS - set(row.keys())
    if missing_fields:
        return False, f"필수 필드 누락: {missing_fields}"

    for field in REQUIRED_FIELDS:
        if not str(row.get(field, "")).strip():
            return False, f"필드 값 없음: {field}"

    return True, ""


def normalize_log_row(row: dict) -> dict | None:
    """행 데이터를 정규화하고 타입 변환을 수행한다.

    Returns:
        정규화된 dict, timestamp 변환 실패 시 None
    """
    timestamp = _parse_timestamp(row.get("timestamp", ""))
    if timestamp is None:
        return None

    return {
        "timestamp": timestamp,
        "device_type": row.get("device_type", "").strip().upper(),
        "src_ip": row.get("src_ip", "").strip(),
        "src_port": _parse_port(row.get("src_port")),
        "dst_ip": row.get("dst_ip", "").strip(),
        "dst_port": _parse_port(row.get("dst_port")),
        "protocol": _optional_str(row.get("protocol")),
        "event_type": row.get("event_type", "").strip(),
        "action": _optional_upper(row.get("action")),
        "severity": _optional_upper(row.get("severity")),
        "message": _optional_str(row.get("message")),
        "raw_log": ",".join(str(v) for v in row.values()),
    }


def _parse_timestamp(value: str) -> datetime | None:
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    log.warning("timestamp 파싱 실패: value=%s", value)
    return None


def _parse_port(value: str | None) -> int | None:
    if not value or not str(value).strip():
        return None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _optional_str(value: str | None) -> str | None:
    if not value:
        return None
    stripped = str(value).strip()
    return stripped or None


def _optional_upper(value: str | None) -> str | None:
    result = _optional_str(value)
    return result.upper() if result else None
