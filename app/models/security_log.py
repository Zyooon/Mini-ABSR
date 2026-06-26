import enum
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DeviceType(str, enum.Enum):
    FW = "FW"
    WAF = "WAF"
    IPS = "IPS"

    @classmethod
    def from_name(cls, name: str | None) -> "DeviceType | None":
        if name is None:
            return None
        try:
            return cls[name.strip().upper()]
        except KeyError:
            return None


class EventType(str, enum.Enum):
    PORT_SCAN = "PORT_SCAN"
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    BRUTE_FORCE = "BRUTE_FORCE"
    SIGNATURE_HIT = "SIGNATURE_HIT"
    MALICIOUS_BOT = "MALICIOUS_BOT"
    DDOS_PATTERN = "DDoS_PATTERN"
    NORMAL_ACCESS = "NORMAL_ACCESS"
    NORMAL_REQUEST = "NORMAL_REQUEST"

    @classmethod
    def from_name(cls, name: str | None) -> "EventType | None":
        if name is None:
            return None
        try:
            return cls[name.strip().upper()]
        except KeyError:
            return None


class Action(str, enum.Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    BLOCK = "BLOCK"

    @classmethod
    def from_name(cls, name: str | None) -> "Action | None":
        if name is None:
            return None
        try:
            return cls[name.strip().upper()]
        except KeyError:
            return None


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_name(cls, name: str | None) -> "Severity | None":
        if name is None:
            return None
        try:
            return cls[name.strip().upper()]
        except KeyError:
            return None


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    device_type: Mapped[str] = mapped_column(String(20), nullable=False)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    src_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dst_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    dst_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str | None] = mapped_column(String(20), nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    incident_links: Mapped[list["IncidentLog"]] = relationship(  # noqa: F821
        back_populates="log"
    )

    __table_args__ = (
        Index("ix_security_logs_src_ip", "src_ip"),
        Index("ix_security_logs_timestamp", "timestamp"),
        Index("ix_security_logs_event_type", "event_type"),
    )
