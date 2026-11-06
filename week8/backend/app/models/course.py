import uuid
from sqlalchemy import CheckConstraint, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
class Course(Base):
    __tablename__="courses"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    name: Mapped[str]=mapped_column(String(100),nullable=False)
    semester: Mapped[str]=mapped_column(String(50),nullable=False)
    teacher: Mapped[str]=mapped_column(String(80),nullable=False,default="")
    location: Mapped[str]=mapped_column(String(100),nullable=False,default="")
    color: Mapped[str]=mapped_column(String(7),nullable=False,default="#315fd2")
class CourseSession(Base):
    __tablename__="course_sessions"
    __table_args__=(CheckConstraint("weekday BETWEEN 1 AND 7",name="ck_course_sessions_weekday"),CheckConstraint("end_time > start_time",name="ck_course_sessions_time"),UniqueConstraint("course_id","weekday","start_time","end_time",name="uq_course_session"))
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    course_id: Mapped[str]=mapped_column(ForeignKey("courses.id",ondelete="CASCADE"),nullable=False,index=True)
    weekday: Mapped[int]=mapped_column(nullable=False)
    start_time: Mapped[object]=mapped_column(Time,nullable=False)
    end_time: Mapped[object]=mapped_column(Time,nullable=False)
