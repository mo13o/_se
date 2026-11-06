from datetime import time
from fastapi import APIRouter,Depends,HTTPException,Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import current_user,require_csrf
from app.db.session import get_db
from app.models.course import Course,CourseSession
from app.models.user import User
from app.schemas.auth_course import CourseInput,SessionInput
router=APIRouter(prefix="/courses",tags=["courses"])
def own(course_id,user,db):
    item=db.scalar(select(Course).where(Course.id==course_id,Course.user_id==user.id))
    if not item: raise HTTPException(404,detail={"code":"COURSE_NOT_FOUND","message":"找不到課程","details":{}})
    return item
def view(c): return {"id":c.id,"name":c.name,"semester":c.semester,"teacher":c.teacher,"location":c.location,"color":c.color}
@router.get("")
def list_courses(user:User=Depends(current_user),db:Session=Depends(get_db)): return {"data":[view(c) for c in db.scalars(select(Course).where(Course.user_id==user.id).order_by(Course.name)).all()]}
@router.post("",status_code=201,dependencies=[Depends(require_csrf)])
def create(payload:CourseInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
    c=Course(user_id=user.id,**payload.model_dump());db.add(c);db.commit();db.refresh(c);return {"data":view(c)}
@router.patch("/{course_id}",dependencies=[Depends(require_csrf)])
def update(course_id:str,payload:CourseInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
    c=own(course_id,user,db)
    for k,v in payload.model_dump().items(): setattr(c,k,v)
    db.commit();return {"data":view(c)}
@router.delete("/{course_id}",status_code=204,dependencies=[Depends(require_csrf)])
def remove(course_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)): db.delete(own(course_id,user,db));db.commit();return Response(status_code=204)
@router.get("/{course_id}/sessions")
def sessions(course_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    own(course_id,user,db); items=db.scalars(select(CourseSession).where(CourseSession.course_id==course_id).order_by(CourseSession.weekday,CourseSession.start_time)).all();return {"data":[{"id":s.id,"weekday":s.weekday,"start_time":s.start_time.isoformat(timespec="minutes"),"end_time":s.end_time.isoformat(timespec="minutes")} for s in items]}
@router.post("/{course_id}/sessions",status_code=201,dependencies=[Depends(require_csrf)])
def add_session(course_id:str,payload:SessionInput,user:User=Depends(current_user),db:Session=Depends(get_db)):
    own(course_id,user,db); start=time.fromisoformat(payload.start_time); end=time.fromisoformat(payload.end_time)
    if end<=start: raise HTTPException(422,detail={"code":"TIME_INVALID","message":"結束時間必須晚於開始時間","details":{}})
    overlap=db.scalar(select(CourseSession).join(Course).where(Course.user_id==user.id,CourseSession.weekday==payload.weekday,CourseSession.start_time<end,CourseSession.end_time>start))
    if overlap and not payload.confirm_overlap: raise HTTPException(409,detail={"code":"SCHEDULE_OVERLAP","message":"此時段與既有課程重疊；確認後可保存","details":{"confirm_overlap":True}})
    item=CourseSession(course_id=course_id,weekday=payload.weekday,start_time=start,end_time=end);db.add(item);db.commit();db.refresh(item);return {"data":{"id":item.id,"weekday":item.weekday,"start_time":payload.start_time,"end_time":payload.end_time},"overlap_confirmed":bool(overlap)}
@router.delete("/{course_id}/sessions/{session_id}",status_code=204,dependencies=[Depends(require_csrf)])
def delete_session(course_id:str,session_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    own(course_id,user,db);item=db.scalar(select(CourseSession).where(CourseSession.id==session_id,CourseSession.course_id==course_id))
    if not item: raise HTTPException(404,detail={"code":"SESSION_NOT_FOUND","message":"找不到課程時段","details":{}})
    db.delete(item);db.commit();return Response(status_code=204)
