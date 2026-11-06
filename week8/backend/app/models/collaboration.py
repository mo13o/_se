import uuid
from datetime import date,datetime,timezone
from sqlalchemy import Date,DateTime,Float,ForeignKey,Integer,String,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)
class Team(Base):
 __tablename__="teams";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);name:Mapped[str]=mapped_column(String(100));description:Mapped[str]=mapped_column(Text,default="");created_by:Mapped[str]=mapped_column(ForeignKey("users.id"));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class TeamMember(Base):
 __tablename__="team_members";__table_args__=(UniqueConstraint("team_id","user_id",name="uq_team_member"),);id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);team_id:Mapped[str]=mapped_column(ForeignKey("teams.id",ondelete="CASCADE"),index=True);user_id:Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"));role:Mapped[str]=mapped_column(String(10));joined_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class TeamInvite(Base):
 __tablename__="team_invites";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);team_id:Mapped[str]=mapped_column(ForeignKey("teams.id",ondelete="CASCADE"));token_hash:Mapped[str]=mapped_column(String(64),unique=True);expires_at:Mapped[datetime]=mapped_column(DateTime(timezone=True));max_uses:Mapped[int]=mapped_column(Integer,default=1);used_count:Mapped[int]=mapped_column(Integer,default=0);created_by:Mapped[str]=mapped_column(ForeignKey("users.id"))
class Project(Base):
 __tablename__="projects";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);team_id:Mapped[str]=mapped_column(ForeignKey("teams.id",ondelete="CASCADE"),index=True);name:Mapped[str]=mapped_column(String(100));description:Mapped[str]=mapped_column(Text,default="");start_date:Mapped[date]=mapped_column(Date);due_date:Mapped[date]=mapped_column(Date);status:Mapped[str]=mapped_column(String(20),default="active")
class Milestone(Base):
 __tablename__="milestones";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);project_id:Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE"),index=True);title:Mapped[str]=mapped_column(String(100));due_date:Mapped[date]=mapped_column(Date);status:Mapped[str]=mapped_column(String(20),default="pending")
class ProjectTask(Base):
 __tablename__="project_tasks";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);project_id:Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE"),index=True);created_by:Mapped[str]=mapped_column(ForeignKey("users.id"));assignee_id:Mapped[str|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"));title:Mapped[str]=mapped_column(String(100));description:Mapped[str]=mapped_column(Text,default="");priority:Mapped[str]=mapped_column(String(10),default="medium");status:Mapped[str]=mapped_column(String(20),default="todo");start_date:Mapped[date|None]=mapped_column(Date);due_date:Mapped[date]=mapped_column(Date);estimated_hours:Mapped[float|None]=mapped_column(Float);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now);updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now);completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class TaskComment(Base):
 __tablename__="task_comments";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);task_id:Mapped[str]=mapped_column(ForeignKey("project_tasks.id",ondelete="CASCADE"),index=True);author_id:Mapped[str]=mapped_column(ForeignKey("users.id"));body:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class AuditLog(Base):
 __tablename__="audit_logs";id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid);actor_id:Mapped[str]=mapped_column(ForeignKey("users.id"));team_id:Mapped[str|None]=mapped_column(ForeignKey("teams.id",ondelete="SET NULL"));action:Mapped[str]=mapped_column(String(50));entity_type:Mapped[str]=mapped_column(String(30));entity_id:Mapped[str]=mapped_column(String(36));created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
