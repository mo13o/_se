from datetime import date,datetime,timedelta,timezone
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import current_user,require_csrf
from app.db.session import get_db
from app.models.course import Course,CourseSession
from app.models.notification import Notification
from app.models.task import Task
from app.models.user import User
router=APIRouter(tags=["calendar","notifications"])
def generate(db,user):
 today=date.today()
 for task in db.scalars(select(Task).where(Task.owner_id==user.id,Task.status=="todo",Task.due_date<=today+timedelta(days=3))).all():
  kind="overdue" if task.due_date<today else "due_soon";key=f"task:{task.id}:{kind}:{task.due_date}";db.add(Notification(user_id=user.id,kind=kind,entity_type="task",entity_id=task.id,dedupe_key=key,message=f"{task.title} {'已逾期' if kind=='overdue' else '即將到期'}"))
 try: db.commit()
 except IntegrityError: db.rollback()
@router.get("/calendar/events")
def events(from_:date=Query(alias="from"),to:date=Query(),user:User=Depends(current_user),db:Session=Depends(get_db)):
 if (to-from_).days>93 or to<from_: raise HTTPException(422,detail={"code":"DATE_RANGE_INVALID","message":"日期區間最多 93 天","details":{}})
 tasks=db.scalars(select(Task).where(Task.owner_id==user.id,Task.due_date>=from_,Task.due_date<=to)).all();sessions=db.execute(select(CourseSession,Course).join(Course).where(Course.user_id==user.id)).all()
 return {"data":[{"id":t.id,"type":"task","title":t.title,"date":t.due_date,"status":t.status} for t in tasks]+[{"id":s.id,"type":"course","title":c.name,"weekday":s.weekday,"start_time":s.start_time,"end_time":s.end_time} for s,c in sessions]}
@router.get("/notifications")
def notifications(user:User=Depends(current_user),db:Session=Depends(get_db)):
 generate(db,user);items=db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc())).all();return {"data":[{"id":n.id,"kind":n.kind,"message":n.message,"read_at":n.read_at,"created_at":n.created_at} for n in items]}
@router.patch("/notifications/{notification_id}/read",dependencies=[Depends(require_csrf)])
def read(notification_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 n=db.scalar(select(Notification).where(Notification.id==notification_id,Notification.user_id==user.id))
 if not n: raise HTTPException(404,detail={"code":"NOTIFICATION_NOT_FOUND","message":"找不到通知","details":{}})
 n.read_at=datetime.now(timezone.utc);db.commit();return {"data":{"id":n.id,"read_at":n.read_at}}
