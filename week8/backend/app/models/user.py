import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    email: Mapped[str]=mapped_column(String(254),unique=True,index=True,nullable=False)
    password_hash: Mapped[str]=mapped_column(String(255),nullable=False)
    display_name: Mapped[str]=mapped_column(String(80),nullable=False)
    timezone: Mapped[str]=mapped_column(String(50),nullable=False,default="Asia/Taipei")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,nullable=False)
class AuthSession(Base):
    __tablename__="auth_sessions"
    id: Mapped[str]=mapped_column(String(64),primary_key=True)
    user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    csrf_token: Mapped[str]=mapped_column(String(64),nullable=False)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)

