from datetime import date,datetime,timezone
from fastapi import APIRouter,Depends,HTTPException,Response
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.core.security import current_user,require_csrf
from app.db.session import get_db
from app.models.collaboration import Project,ProjectTask,TaskComment,TeamMember
from app.models.user import User
from app.api.v1.teams_projects import membership,project_access
router=APIRouter(tags=["project tasks"])
class TaskIn(BaseModel):title:str=Field(min_length=1,max_length=100);description:str="";priority:str="medium";status:str="todo";start_date:date|None=None;due_date:date;estimated_hours:float|None=None;assignee_id:str|None=None
class CommentIn(BaseModel):body:str=Field(min_length=1,max_length=2000)
def access_task(tid,user,db):
 t=db.get(ProjectTask,tid)
 if not t:raise HTTPException(404,detail={"code":"TASK_NOT_FOUND","message":"找不到團隊任務","details":{}})
 p=project_access(t.project_id,user,db);return t,p
def view(t):return {"id":t.id,"project_id":t.project_id,"title":t.title,"description":t.description,"priority":t.priority,"status":t.status,"start_date":t.start_date,"due_date":t.due_date,"estimated_hours":t.estimated_hours,"assignee_id":t.assignee_id,"created_by":t.created_by,"completed_at":t.completed_at}
@router.get("/projects/{project_id}/tasks")
def tasks(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):project_access(project_id,user,db);return {"data":[view(t) for t in db.scalars(select(ProjectTask).where(ProjectTask.project_id==project_id).order_by(ProjectTask.due_date)).all()]}
@router.post("/projects/{project_id}/tasks",status_code=201,dependencies=[Depends(require_csrf)])
def create(project_id:str,payload:TaskIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 p=project_access(project_id,user,db)
 if payload.start_date and payload.start_date>payload.due_date:raise HTTPException(422,detail="date invalid")
 if payload.assignee_id and not db.scalar(select(TeamMember).where(TeamMember.team_id==p.team_id,TeamMember.user_id==payload.assignee_id)):raise HTTPException(422,detail={"code":"ASSIGNEE_INVALID","message":"負責人不是團隊成員","details":{}})
 t=ProjectTask(project_id=project_id,created_by=user.id,**payload.model_dump());db.add(t);db.commit();db.refresh(t);return {"data":view(t)}
@router.patch("/project-tasks/{task_id}",dependencies=[Depends(require_csrf)])
def update(task_id:str,payload:dict,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t,p=access_task(task_id,user,db);m=membership(p.team_id,user,db)
 if m.role=="member" and user.id not in {t.created_by,t.assignee_id}:raise HTTPException(403,detail={"code":"TASK_FORBIDDEN","message":"只能修改自己建立或被指派的任務","details":{}})
 allowed={"title","description","priority","status","start_date","due_date","estimated_hours","assignee_id"}
 if payload.get("status") not in {None,"todo","in_progress","review","done"}:raise HTTPException(422,detail="status invalid")
 if "assignee_id" in payload and payload["assignee_id"] and not db.scalar(select(TeamMember).where(TeamMember.team_id==p.team_id,TeamMember.user_id==payload["assignee_id"])):raise HTTPException(422,detail="assignee invalid")
 for k,v in payload.items():
  if k in allowed:setattr(t,k,v)
 t.completed_at=datetime.now(timezone.utc) if t.status=="done" else None;t.updated_at=datetime.now(timezone.utc);db.commit();db.refresh(t);return {"data":view(t)}
@router.patch("/project-tasks/{task_id}/status",dependencies=[Depends(require_csrf)])
def status(task_id:str,payload:dict,user:User=Depends(current_user),db:Session=Depends(get_db)):return update(task_id,{"status":payload.get("status")},user,db)
@router.get("/project-tasks/{task_id}/comments")
def comments(task_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 access_task(task_id,user,db);return {"data":[{"id":c.id,"author_id":c.author_id,"body":c.body,"created_at":c.created_at} for c in db.scalars(select(TaskComment).where(TaskComment.task_id==task_id)).all()]}
@router.post("/project-tasks/{task_id}/comments",status_code=201,dependencies=[Depends(require_csrf)])
def comment(task_id:str,payload:CommentIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 access_task(task_id,user,db);c=TaskComment(task_id=task_id,author_id=user.id,body=payload.body.strip());db.add(c);db.commit();db.refresh(c);return {"data":{"id":c.id,"body":c.body}}
@router.delete("/task-comments/{comment_id}",status_code=204,dependencies=[Depends(require_csrf)])
def delete_comment(comment_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 c=db.get(TaskComment,comment_id)
 if not c:raise HTTPException(404,detail="not found")
 t,p=access_task(c.task_id,user,db);m=membership(p.team_id,user,db)
 if c.author_id!=user.id and m.role not in {"owner","admin"}:raise HTTPException(403,detail="forbidden")
 db.delete(c);db.commit();return Response(status_code=204)
@router.get("/projects/{project_id}/summary")
def summary(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 project_access(project_id,user,db);items=db.scalars(select(ProjectTask).where(ProjectTask.project_id==project_id)).all();counts={s:sum(t.status==s for t in items) for s in ["todo","in_progress","review","done"]};total=len(items);return {"data":{"total":total,**counts,"overdue":sum(t.status!="done" and t.due_date<date.today() for t in items),"completion_rate":round(counts["done"]/total*100) if total else 0}}
