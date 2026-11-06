import hashlib, secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Cookie, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import AuthSession, User
ph=PasswordHasher()
def hash_password(value:str)->str: return ph.hash(value)
def verify_password(hashed:str,value:str)->bool:
    try: return ph.verify(hashed,value)
    except VerifyMismatchError: return False
def token_hash(value:str)->str: return hashlib.sha256(value.encode()).hexdigest()
def create_session(db:Session,user_id:str):
    raw=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(24)
    db.add(AuthSession(id=token_hash(raw),user_id=user_id,csrf_token=csrf,expires_at=datetime.now(timezone.utc)+timedelta(days=7))); db.commit(); return raw,csrf
def current_session(taskflow_session:str|None=Cookie(default=None),db:Session=Depends(get_db)):
    if not taskflow_session: raise HTTPException(401,detail={"code":"UNAUTHENTICATED","message":"請先登入","details":{}})
    session=db.get(AuthSession,token_hash(taskflow_session))
    if not session or session.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(401,detail={"code":"SESSION_INVALID","message":"登入已失效","details":{}})
    return session
def current_user(session:AuthSession=Depends(current_session),db:Session=Depends(get_db))->User:
    user=db.get(User,session.user_id)
    if not user: raise HTTPException(401,detail={"code":"UNAUTHENTICATED","message":"請先登入","details":{}})
    return user
def require_csrf(x_csrf_token:str|None=Header(default=None),session:AuthSession=Depends(current_session)):
    if not x_csrf_token or not secrets.compare_digest(x_csrf_token,session.csrf_token): raise HTTPException(403,detail={"code":"CSRF_INVALID","message":"安全驗證失敗","details":{}})
    return session
