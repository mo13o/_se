import csv,io
from datetime import date
from fastapi import APIRouter,Depends,Query
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import current_user
from app.db.session import get_db
from app.models.collaboration import Milestone,ProjectTask
from app.models.user import User
from app.api.v1.teams_projects import project_access
router=APIRouter(tags=["reports"])
@router.get("/projects/{project_id}/tasks.csv")
def export_csv(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 project_access(project_id,user,db);items=db.scalars(select(ProjectTask).where(ProjectTask.project_id==project_id)).all();stream=io.StringIO();w=csv.writer(stream);w.writerow(["任務","狀態","優先級","開始日","截止日","負責人","預估工時"])
 for t in items:
  assignee=db.get(User,t.assignee_id).display_name if t.assignee_id and db.get(User,t.assignee_id) else ""
  w.writerow([t.title,t.status,t.priority,t.start_date or "",t.due_date,assignee,t.estimated_hours or ""])
 return Response(content='\ufeff'+stream.getvalue(),media_type="text/csv; charset=utf-8",headers={"Content-Disposition":f'attachment; filename="project-{project_id}.csv"'})
@router.get("/projects/{project_id}/reports/weekly.pdf")
def weekly(project_id:str,from_:date=Query(alias="from"),to:date=Query(),user:User=Depends(current_user),db:Session=Depends(get_db)):
 p=project_access(project_id,user,db);items=db.scalars(select(ProjectTask).where(ProjectTask.project_id==project_id)).all();milestones=db.scalars(select(Milestone).where(Milestone.project_id==project_id,Milestone.due_date>=from_,Milestone.due_date<=to)).all();buf=io.BytesIO();pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'));c=canvas.Canvas(buf,pagesize=A4);c.setFont('STSong-Light',16);c.drawString(50,800,f"{p.name} 週報");c.setFont('STSong-Light',10);c.drawString(50,780,f"期間：{from_} ～ {to}  任務總數：{len(items)}  完成：{sum(t.status=='done' for t in items)}  逾期：{sum(t.status!='done' and t.due_date<date.today() for t in items)}");y=750
 for t in items:
  c.drawString(60,y,f"• {t.title}｜{t.status}｜截止 {t.due_date}");y-=18
  if y<80:c.showPage();c.setFont('STSong-Light',10);y=800
 if milestones:c.drawString(50,y-10,"里程碑："+"、".join(m.title for m in milestones))
 c.save();return Response(content=buf.getvalue(),media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="weekly-{project_id}.pdf"'})
