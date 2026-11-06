import uuid
from datetime import datetime,timezone
from sqlalchemy import DateTime,ForeignKey,String,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
class Notification(Base):
    __tablename__="notifications";__table_args__=(UniqueConstraint("user_id","dedupe_key",name="uq_notification_dedupe"),)
    id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()));user_id:Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),index=True);kind:Mapped[str]=mapped_column(String(30));entity_type:Mapped[str]=mapped_column(String(30));entity_id:Mapped[str]=mapped_column(String(36));dedupe_key:Mapped[str]=mapped_column(String(200));message:Mapped[str]=mapped_column(String(300));read_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
