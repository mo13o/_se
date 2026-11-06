from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.security import current_user
from app.db.session import get_db
from app.models.user import User
from app.services.task_stats import task_summary
router=APIRouter(prefix="/dashboard",tags=["dashboard"])
@router.get("/summary")
def summary(user:User=Depends(current_user),db:Session=Depends(get_db)): return {"data":task_summary(db,owner_id=user.id)}
