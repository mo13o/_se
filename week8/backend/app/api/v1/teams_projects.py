import hashlib,secrets
from datetime import date,datetime,timedelta,timezone
from fastapi import APIRouter,Depends,HTTPException,Response
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import current_user,require_csrf
from app.db.session import get_db
from app.models.collaboration import Milestone,Project,Team,TeamInvite,TeamMember
from app.models.user import User
router=APIRouter(tags=["teams","projects"])
class TeamIn(BaseModel):name:str=Field(min_length=1,max_length=100);description:str=Field(default="",max_length=1000)
class ProjectIn(BaseModel):name:str;description:str="";start_date:date;due_date:date;status:str="active"
class MilestoneIn(BaseModel):title:str;due_date:date;status:str="pending"
def membership(team_id,user,db,roles=None):
 m=db.scalar(select(TeamMember).where(TeamMember.team_id==team_id,TeamMember.user_id==user.id))
 if not m or roles and m.role not in roles: raise HTTPException(404 if not m else 403,detail={"code":"TEAM_FORBIDDEN","message":"無法存取此團隊","details":{}})
 return m
def project_access(pid,user,db):
 p=db.get(Project,pid)
 if not p: raise HTTPException(404,detail={"code":"PROJECT_NOT_FOUND","message":"找不到專案","details":{}})
 membership(p.team_id,user,db);return p
@router.get("/teams")
def teams(user:User=Depends(current_user),db:Session=Depends(get_db)):
 rows=db.execute(select(Team,TeamMember).join(TeamMember).where(TeamMember.user_id==user.id)).all();return {"data":[{"id":t.id,"name":t.name,"description":t.description,"role":m.role} for t,m in rows]}
@router.post("/teams",status_code=201,dependencies=[Depends(require_csrf)])
def create_team(payload:TeamIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t=Team(name=payload.name,description=payload.description,created_by=user.id);db.add(t);db.flush();db.add(TeamMember(team_id=t.id,user_id=user.id,role="owner"));db.commit();return {"data":{"id":t.id,"name":t.name,"role":"owner"}}
@router.get("/teams/{team_id}/members")
def members(team_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(team_id,user,db);rows=db.execute(select(TeamMember,User).join(User,User.id==TeamMember.user_id).where(TeamMember.team_id==team_id)).all();return {"data":[{"user_id":u.id,"display_name":u.display_name,"email":u.email,"role":m.role} for m,u in rows]}
@router.post("/teams/{team_id}/invites",dependencies=[Depends(require_csrf)])
def invite(team_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(team_id,user,db,{"owner","admin"});raw=secrets.token_urlsafe(24);item=TeamInvite(team_id=team_id,token_hash=hashlib.sha256(raw.encode()).hexdigest(),expires_at=datetime.now(timezone.utc)+timedelta(days=7),max_uses=10,used_count=0,created_by=user.id);db.add(item);db.commit();return {"data":{"token":raw,"expires_at":item.expires_at}}
@router.post("/team-invites/accept",dependencies=[Depends(require_csrf)])
def accept(payload:dict,user:User=Depends(current_user),db:Session=Depends(get_db)):
 token=hashlib.sha256(str(payload.get("token","")).encode()).hexdigest();i=db.scalar(select(TeamInvite).where(TeamInvite.token_hash==token))
 if not i or i.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc) or i.used_count>=i.max_uses: raise HTTPException(409,detail={"code":"INVITE_INVALID","message":"邀請無效、過期或已達使用上限","details":{}})
 if not db.scalar(select(TeamMember).where(TeamMember.team_id==i.team_id,TeamMember.user_id==user.id)):db.add(TeamMember(team_id=i.team_id,user_id=user.id,role="member"));i.used_count+=1;db.commit()
 return {"data":{"team_id":i.team_id}}
@router.patch("/teams/{team_id}/members/{user_id}",dependencies=[Depends(require_csrf)])
def role(team_id:str,user_id:str,payload:dict,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(team_id,user,db,{"owner"});m=db.scalar(select(TeamMember).where(TeamMember.team_id==team_id,TeamMember.user_id==user_id))
 if not m or m.role=="owner":raise HTTPException(409,detail={"code":"OWNER_PROTECTED","message":"不能直接變更 Owner","details":{}})
 if payload.get("role") not in {"admin","member"}:raise HTTPException(422,detail="role invalid")
 m.role=payload["role"];db.commit();return {"data":{"user_id":m.user_id,"role":m.role}}
@router.get("/teams/{team_id}/projects")
def projects(team_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(team_id,user,db);return {"data":[{"id":p.id,"name":p.name,"description":p.description,"start_date":p.start_date,"due_date":p.due_date,"status":p.status} for p in db.scalars(select(Project).where(Project.team_id==team_id)).all()]}
@router.post("/teams/{team_id}/projects",status_code=201,dependencies=[Depends(require_csrf)])
def create_project(team_id:str,payload:ProjectIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(team_id,user,db,{"owner","admin"});
 if payload.due_date<payload.start_date:raise HTTPException(422,detail="date invalid")
 p=Project(team_id=team_id,**payload.model_dump());db.add(p);db.commit();db.refresh(p);return {"data":{"id":p.id,"name":p.name}}
@router.get("/projects/{project_id}")
def project(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 p=project_access(project_id,user,db);return {"data":{"id":p.id,"team_id":p.team_id,"name":p.name,"description":p.description,"start_date":p.start_date,"due_date":p.due_date,"status":p.status}}
@router.get("/projects/{project_id}/milestones")
def milestones(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 project_access(project_id,user,db);return {"data":[{"id":m.id,"title":m.title,"due_date":m.due_date,"status":m.status} for m in db.scalars(select(Milestone).where(Milestone.project_id==project_id)).all()]}
@router.post("/projects/{project_id}/milestones",status_code=201,dependencies=[Depends(require_csrf)])
def create_milestone(project_id:str,payload:MilestoneIn,user:User=Depends(current_user),db:Session=Depends(get_db)):
 p=project_access(project_id,user,db);membership(p.team_id,user,db,{"owner","admin"});m=Milestone(project_id=project_id,**payload.model_dump());db.add(m);db.commit();db.refresh(m);return {"data":{"id":m.id,"title":m.title}}
