from datetime import date,timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.db.session import get_db
from app.main import app
engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Session=sessionmaker(bind=engine,expire_on_commit=False)
def override_db():
    db=Session()
    try: yield db
    finally: db.close()
app.dependency_overrides[get_db]=override_db;client=TestClient(app)
@pytest.fixture(autouse=True)
def clean():
    client.cookies.clear();Base.metadata.drop_all(engine);Base.metadata.create_all(engine)
def register(email="a@example.com"):
    result=client.post("/api/v1/auth/register",json={"email":email,"password":"SecurePass123","display_name":"測試者"});assert result.status_code==201;return result.json()["csrf_token"]
def headers(csrf): return {"X-CSRF-Token":csrf}
def payload(title="資料庫作業",days=1,**changes):
    data={"title":title,"description":"SQL","category":"assignment","priority":"high","status":"todo","due_date":str(date.today()+timedelta(days=days)),"course_id":None};data.update(changes);return data
def test_auth_task_crud_search_summary():
    csrf=register(); created=client.post("/api/v1/tasks",json=payload(),headers=headers(csrf)).json()["data"];tid=created["id"]
    assert client.get(f"/api/v1/tasks/{tid}").status_code==200
    assert client.patch(f"/api/v1/tasks/{tid}",json={"status":"done"},headers=headers(csrf)).json()["data"]["completed_at"]
    assert client.get("/api/v1/dashboard/summary").json()["data"]["done"]==1
    assert client.delete(f"/api/v1/tasks/{tid}",headers=headers(csrf)).status_code==204
def test_two_users_cannot_see_each_others_tasks():
    csrf=register("a@example.com");tid=client.post("/api/v1/tasks",json=payload(),headers=headers(csrf)).json()["data"]["id"]
    client.cookies.clear();register("b@example.com")
    assert client.get("/api/v1/tasks").json()["meta"]["total"]==0
    assert client.get(f"/api/v1/tasks/{tid}").status_code==404
def test_course_sessions_overlap_requires_confirmation_and_task_link():
    csrf=register();course=client.post("/api/v1/courses",json={"name":"資料庫","semester":"115-1","teacher":"王老師","location":"A101","color":"#315fd2"},headers=headers(csrf)).json()["data"]
    first={"weekday":1,"start_time":"09:00","end_time":"10:00"};assert client.post(f"/api/v1/courses/{course['id']}/sessions",json=first,headers=headers(csrf)).status_code==201
    overlap={"weekday":1,"start_time":"09:30","end_time":"10:30"};assert client.post(f"/api/v1/courses/{course['id']}/sessions",json=overlap,headers=headers(csrf)).status_code==409
    overlap["confirm_overlap"]=True;assert client.post(f"/api/v1/courses/{course['id']}/sessions",json=overlap,headers=headers(csrf)).status_code==201
    task=client.post("/api/v1/tasks",json=payload(course_id=course["id"]),headers=headers(csrf));assert task.status_code==201 and task.json()["data"]["course_id"]==course["id"]
def test_auth_validation_csrf_and_password_change():
    assert client.get("/api/v1/tasks").status_code==401
    csrf=register();assert client.post("/api/v1/tasks",json=payload()).status_code==403
    assert client.post("/api/v1/users/me/change-password",json={"current_password":"SecurePass123","new_password":"NewSecure456"},headers=headers(csrf)).status_code==204


def switch_session(raw):
    client.cookies.clear();client.cookies.set("taskflow_session",raw)
    return client.get("/api/v1/auth/me").json()["csrf_token"]

def test_p3_calendar_notification_dedupe_and_read():
    csrf=register();client.post("/api/v1/tasks",json=payload("明日作業",1),headers=headers(csrf))
    events=client.get("/api/v1/calendar/events",params={"from":str(date.today()),"to":str(date.today()+timedelta(days=7))})
    assert events.status_code==200 and any(x["type"]=="task" for x in events.json()["data"])
    first=client.get("/api/v1/notifications").json()["data"];second=client.get("/api/v1/notifications").json()["data"]
    assert len(first)==len(second)==1
    assert client.patch(f"/api/v1/notifications/{first[0]['id']}/read",headers=headers(csrf)).status_code==200

def test_p4_to_p6_team_workflow_permissions_board_comments_and_reports():
    a_csrf=register("owner@example.com");a_session=client.cookies.get("taskflow_session")
    team=client.post("/api/v1/teams",json={"name":"畢業專題","description":"測試"},headers=headers(a_csrf)).json()["data"]
    invite_token=client.post(f"/api/v1/teams/{team['id']}/invites",headers=headers(a_csrf)).json()["data"]["token"]
    client.cookies.clear();b_csrf=register("member@example.com");b_session=client.cookies.get("taskflow_session")
    assert client.post("/api/v1/team-invites/accept",json={"token":invite_token},headers=headers(b_csrf)).status_code==200
    switch_session(a_session);project=client.post(f"/api/v1/teams/{team['id']}/projects",json={"name":"TaskFlow","description":"","start_date":"2026-10-01","due_date":"2026-12-31","status":"active"},headers=headers(a_csrf)).json()["data"]
    members=client.get(f"/api/v1/teams/{team['id']}/members").json()["data"];member_id=next(x["user_id"] for x in members if x["email"]=="member@example.com")
    task=client.post(f"/api/v1/projects/{project['id']}/tasks",json={"title":"完成看板","description":"","priority":"high","status":"todo","start_date":"2026-10-30","due_date":"2026-11-10","estimated_hours":4,"assignee_id":member_id},headers=headers(a_csrf)).json()["data"]
    switch_session(b_session);b_csrf=client.get("/api/v1/auth/me").json()["csrf_token"]
    assert client.patch(f"/api/v1/project-tasks/{task['id']}/status",json={"status":"in_progress"},headers=headers(b_csrf)).json()["data"]["status"]=="in_progress"
    assert client.post(f"/api/v1/project-tasks/{task['id']}/comments",json={"body":"已開始處理"},headers=headers(b_csrf)).status_code==201
    client.cookies.clear();register("outsider@example.com")
    assert client.get(f"/api/v1/projects/{project['id']}/tasks").status_code==404
    switch_session(a_session)
    csv_response=client.get(f"/api/v1/projects/{project['id']}/tasks.csv");pdf=client.get(f"/api/v1/projects/{project['id']}/reports/weekly.pdf",params={"from":"2026-10-01","to":"2026-12-31"})
    assert csv_response.status_code==200 and "text/csv" in csv_response.headers["content-type"]
    assert pdf.status_code==200 and pdf.content.startswith(b"%PDF")
    assert client.get(f"/api/v1/projects/{project['id']}/summary").json()["data"]["in_progress"]==1
