"""Create fictional demo data. Never use real student information."""
from datetime import date,timedelta
from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.models.task import Task
with SessionLocal.begin() as db:
 user=db.scalar(select(User).where(User.email=="demo@taskflow.local"))
 if not user:
  user=User(email="demo@taskflow.local",password_hash=hash_password("DemoPassword123"),display_name="示範學生");db.add(user);db.flush()
 if not db.scalar(select(Task).where(Task.owner_id==user.id,Task.title=="完成示範作業")):
  db.add(Task(owner_id=user.id,title="完成示範作業",description="虛構測試資料",category="assignment",priority="high",status="todo",due_date=date.today()+timedelta(days=2)))
print("Seed ready: demo@taskflow.local / DemoPassword123")
