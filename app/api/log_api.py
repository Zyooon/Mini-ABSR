import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.security_log import SecurityLog
from app.schemas.log_schema import LogUploadResponse
from app.services.log_parser import normalize_log_row, parse_csv_bytes, validate_log_row

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.post("/upload", response_model=LogUploadResponse)
async def upload_logs(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> LogUploadResponse:
    """보안 로그 CSV 파일을 업로드하고 DB에 저장한다.

    Args:
        file: CSV 형식의 보안 로그 파일

    Raises:
        HTTPException: CSV 파일이 아닌 경우
    """
    if not (file.filename or "").endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")

    content = await file.read()
    rows = parse_csv_bytes(content)

    saved_count = 0
    skipped_count = 0
    errors: list[str] = []

    for line_number, row in enumerate(rows, start=2):
        is_valid, error_message = validate_log_row(row)
        if not is_valid:
            skipped_count += 1
            errors.append(f"행 {line_number}: {error_message}")
            continue

        normalized = normalize_log_row(row)
        if normalized is None:
            skipped_count += 1
            errors.append(
                f"행 {line_number}: timestamp 형식 오류 - {row.get('timestamp')}"
            )
            continue

        db.add(SecurityLog(**normalized))
        saved_count += 1

    if saved_count > 0:
        db.commit()

    log.info(
        "로그 업로드 완료: filename=%s, saved=%s, skipped=%s",
        file.filename,
        saved_count,
        skipped_count,
    )

    return LogUploadResponse(
        saved_count=saved_count,
        skipped_count=skipped_count,
        errors=errors,
    )
