import uuid
from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from database.database import Base


class ECGDatabase(Base):
    __tablename__ = "ecgdatabase"

    id = Column(Integer, primary_key=True, index=True)

    age = Column(Integer, nullable=True)
    history = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)

    ecg_image_path = Column(String, nullable=False)

    # ✅ FIX: UUID foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
