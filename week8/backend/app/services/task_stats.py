from datetime import date, timedelta
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session
from app.models.task import Task

def task_summary(db: Session, today: date | None = None, owner_id: str | None = None) -> dict[str, int]:
    today=today or date.today(); soon=today+timedelta(days=3)
    query=select(
        func.count(Task.id),
        func.sum(case((Task.status=="todo",1),else_=0)),
        func.sum(case((Task.status=="done",1),else_=0)),
        func.sum(case(((Task.status=="todo") & (Task.due_date<today),1),else_=0)),
        func.sum(case(((Task.status=="todo") & (Task.due_date>=today) & (Task.due_date<=soon),1),else_=0)),
    )
    if owner_id: query=query.where(Task.owner_id==owner_id)
    row=db.execute(query).one()
    total=int(row[0] or 0); done=int(row[2] or 0)
    return {"total":total,"todo":int(row[1] or 0),"done":done,"overdue":int(row[3] or 0),"due_soon":int(row[4] or 0),"completion_rate":round(done/total*100) if total else 0}

