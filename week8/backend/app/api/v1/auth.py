from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.core.security import create_session,current_session,current_user,hash_password,require_csrf,verify_password
from app.db.session import get_db
from app.models.user import AuthSession,User
from app.schemas.auth_course import Login,PasswordChange,ProfileUpdate,Register
router=APIRouter(prefix="/auth",tags=["auth"]); attempts=defaultdict(list)
def public(user): return {"id":user.id,"email":user.email,"display_name":user.display_name,"timezone":user.timezone,"created_at":user.created_at}
def set_auth(response,raw,csrf): response.set_cookie("taskflow_session",raw,httponly=True,samesite="lax",secure=False,max_age=604800); response.headers["X-CSRF-Token"]=csrf
@router.post("/register",status_code=201)
def register(payload:Register,response:Response,db:Session=Depends(get_db)):
    email=payload.email.lower().strip()
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,detail={"code":"EMAIL_EXISTS","message":"Email 已被使用","details":{}})
    user=User(email=email,password_hash=hash_password(payload.password),display_name=payload.display_name.strip()); db.add(user); db.commit(); db.refresh(user); raw,csrf=create_session(db,user.id); set_auth(response,raw,csrf); return {"data":public(user),"csrf_token":csrf}
@router.post("/login")
def login(payload:Login,request:Request,response:Response,db:Session=Depends(get_db)):
    key=request.client.host if request.client else "unknown"; now=datetime.now(timezone.utc); attempts[key]=[x for x in attempts[key] if x>now-timedelta(minutes=10)]
    if len(attempts[key])>=8: raise HTTPException(429,detail={"code":"LOGIN_RATE_LIMIT","message":"登入嘗試過多，請稍後再試","details":{}})
    user=db.scalar(select(User).where(User.email==payload.email.lower().strip()))
    if not user or not verify_password(user.password_hash,payload.password): attempts[key].append(now); raise HTTPException(401,detail={"code":"LOGIN_FAILED","message":"Email 或密碼錯誤","details":{}})
    attempts[key]=[]; raw,csrf=create_session(db,user.id); set_auth(response,raw,csrf); return {"data":public(user),"csrf_token":csrf}
@router.post("/logout",status_code=204,dependencies=[Depends(require_csrf)])
def logout(response:Response,session:AuthSession=Depends(current_session),db:Session=Depends(get_db)):
    db.delete(session); db.commit(); response.delete_cookie("taskflow_session"); return response
@router.get("/me")
def me(user:User=Depends(current_user),session:AuthSession=Depends(current_session)): return {"data":public(user),"csrf_token":session.csrf_token}
users=APIRouter(prefix="/users/me",tags=["users"])
@users.patch("",dependencies=[Depends(require_csrf)])
def update_profile(payload:ProfileUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    for key,value in payload.model_dump(exclude_unset=True).items(): setattr(user,key,value.strip())
    db.commit();db.refresh(user);return {"data":public(user)}
@users.post("/change-password",status_code=204,dependencies=[Depends(require_csrf)])
def change_password(payload:PasswordChange,user:User=Depends(current_user),session:AuthSession=Depends(current_session),db:Session=Depends(get_db)):
    if not verify_password(user.password_hash,payload.current_password): raise HTTPException(400,detail={"code":"PASSWORD_WRONG","message":"目前密碼錯誤","details":{}})
    user.password_hash=hash_password(payload.new_password); db.execute(delete(AuthSession).where(AuthSession.user_id==user.id,AuthSession.id!=session.id));db.commit();return Response(status_code=204)
