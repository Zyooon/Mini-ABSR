from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    device_type: str
    src_ip: str
    src_port: int | None
    dst_ip: str
    dst_port: int | None
    protocol: str | None
    event_type: str
    action: str | None
    severity: str | None
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogUploadResponse(BaseModel):
    saved_count: int
    skipped_count: int
    errors: list[str]
