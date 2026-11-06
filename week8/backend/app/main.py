from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.health import router as health_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.auth import router as auth_router, users as users_router
from app.api.v1.courses import router as courses_router
from app.api.v1.calendar_notifications import router as calendar_router
from app.api.v1.teams_projects import router as teams_router
from app.api.v1.project_tasks import router as project_tasks_router
from app.api.v1.reports import router as reports_router
from app.core.config import get_settings
settings=get_settings(); app=FastAPI(title=settings.app_name,version="0.2.0")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(health_router,prefix="/api/v1"); app.include_router(tasks_router,prefix="/api/v1"); app.include_router(dashboard_router,prefix="/api/v1"); app.include_router(auth_router,prefix="/api/v1"); app.include_router(users_router,prefix="/api/v1"); app.include_router(courses_router,prefix="/api/v1"); app.include_router(calendar_router,prefix="/api/v1"); app.include_router(teams_router,prefix="/api/v1"); app.include_router(project_tasks_router,prefix="/api/v1"); app.include_router(reports_router,prefix="/api/v1")
@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422,content={"error":{"code":"VALIDATION_ERROR","message":"輸入資料不正確","details":{"fields":[{key:value for key,value in error.items() if key != "ctx"} for error in exc.errors()]}}})
@app.get("/",include_in_schema=False)
def root(): return {"message":"TaskFlow API","docs":"/docs"}



