from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.db.session import database_is_ready
router=APIRouter(tags=["health"])
@router.get("/health")
def health():
    if not database_is_ready(): raise HTTPException(status_code=503, detail="database unavailable")
    return {"status":"ok","service":get_settings().app_name,"database":"ok"}
