from datetime import datetime,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query,Response
from sqlalchemy import asc,case,desc,func,or_,select
from sqlalchemy.orm import Session
from app.core.security import current_user,require_csrf
from app.db.session import get_db
from app.models.course import Course
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate,TaskRead,TaskUpdate
router=APIRouter(prefix="/tasks",tags=["tasks"])
def find(task_id,user,db):
    task=db.scalar(select(Task).where(Task.id==task_id,Task.owner_id==user.id))
    if not task: raise HTTPException(404,detail={"code":"TASK_NOT_FOUND","message":"找不到任務","details":{}})
    return task
def validate_course(course_id,user,db):
    if course_id and not db.scalar(select(Course.id).where(Course.id==course_id,Course.user_id==user.id)): raise HTTPException(422,detail={"code":"COURSE_INVALID","message":"課程不存在或不屬於你","details":{}})
@router.get("")
def listing(search:str|None=None,category:str|None=None,status:str|None=None,priority:str|None=None,sort:Literal["due_date","priority","created_at"]="due_date",order:Literal["asc","desc"]="asc",limit:int=Query(20,ge=1,le=100),offset:int=Query(0,ge=0),user:User=Depends(current_user),db:Session=Depends(get_db)):
    filters=[Task.owner_id==user.id]
    if search: filters.append(or_(Task.title.ilike(f"%{search.strip()}%"),Task.description.ilike(f"%{search.strip()}%")))
    if category: filters.append(Task.category==category)
    if status: filters.append(Task.status==status)
    if priority: filters.append(Task.priority==priority)
    direction=asc if order=="asc" else desc; query=select(Task).where(*filters)
    if sort=="priority": query=query.order_by(direction(case({"high":0,"medium":1,"low":2},value=Task.priority)),Task.due_date)
    else: query=query.order_by(direction(Task.due_date if sort=="due_date" else Task.created_at),Task.id)
    total=db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0;items=db.scalars(query.offset(offset).limit(limit)).all()
    return {"data":[TaskRead.model_validate(x) for x in items],"meta":{"total":total,"limit":limit,"offset":offset}}
@router.post("",status_code=201,dependencies=[Depends(require_csrf)])
def create(payload:TaskCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    validate_course(payload.course_id,user,db);task=Task(owner_id=user.id,**payload.model_dump());task.completed_at=datetime.now(timezone.utc) if task.status=="done" else None;db.add(task);db.commit();db.refresh(task);return {"data":TaskRead.model_validate(task)}
@router.get("/{task_id}")
def detail(task_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)): return {"data":TaskRead.model_validate(find(task_id,user,db))}
@router.patch("/{task_id}",dependencies=[Depends(require_csrf)])
def update(task_id:str,payload:TaskUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    task=find(task_id,user,db);values=payload.model_dump(exclude_unset=True)
    if "course_id" in values: validate_course(values["course_id"],user,db)
    for k,v in values.items(): setattr(task,k,v)
    if "status" in values: task.completed_at=datetime.now(timezone.utc) if task.status=="done" else None
    task.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(task);return {"data":TaskRead.model_validate(task)}
@router.delete("/{task_id}",status_code=204,dependencies=[Depends(require_csrf)])
def remove(task_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)): db.delete(find(task_id,user,db));db.commit();return Response(status_code=204)
