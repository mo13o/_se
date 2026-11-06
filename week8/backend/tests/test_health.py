from fastapi.testclient import TestClient
from sqlalchemy import text
from app.db.session import build_engine
from app.main import app
def test_health():
    response=TestClient(app).get("/api/v1/health")
    assert response.status_code==200 and response.json()["database"]=="ok"
def test_sqlite_foreign_keys():
    with build_engine("sqlite:///:memory:").connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one()==1
