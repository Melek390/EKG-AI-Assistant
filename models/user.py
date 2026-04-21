import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    institution = Column(String, nullable=True)
    role = Column(
        Enum("doctor", "resident", "admin", name="user_roles"),
        nullable=False,
        default="doctor"
    )
    ecg_records = relationship(
        "ECGDatabase",
        backref="user",
        cascade="all, delete-orphan"
    )
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    last_login = Column(DateTime(timezone=True), nullable=True)
