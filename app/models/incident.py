import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_score(cls, score: int) -> "RiskLevel":
        if score >= 100:
            return cls.CRITICAL
        if score >= 70:
            return cls.HIGH
        if score >= 40:
            return cls.MEDIUM
        return cls.LOW


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    CLOSED = "CLOSED"

    @classmethod
    def from_name(cls, name: str | None) -> "IncidentStatus | None":
        if name is None:
            return None
        try:
            return cls[name.strip().upper()]
        except KeyError:
            return None


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    dst_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=IncidentStatus.OPEN.value, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    log_links: Mapped[list["IncidentLog"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )
    report: Mapped["Report | None"] = relationship(  # noqa: F821
        back_populates="incident", uselist=False
    )


class IncidentLog(Base):
    """Incident와 SecurityLog를 연결하는 중간 테이블."""

    __tablename__ = "incident_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id"), nullable=False
    )
    log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("security_logs.id"), nullable=False
    )

    incident: Mapped["Incident"] = relationship(back_populates="log_links")
    log: Mapped["SecurityLog"] = relationship(  # noqa: F821
        back_populates="incident_links"
    )
