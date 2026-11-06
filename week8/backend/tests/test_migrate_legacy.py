import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from app.db.base import Base
from app.models.task import Task
from scripts.migrate_legacy import import_legacy

def make_legacy(path: Path):
    db=sqlite3.connect(path)
    db.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY,title TEXT,category TEXT,due_date TEXT,priority TEXT,notes TEXT,completed INTEGER,created_at TEXT)")
    db.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?)",[(1,"舊作業","作業","2026-11-01","高","說明",0,"2026-10-30 00:00:00"),(2,"舊考試","考試","2026-11-02","中","",1,"2026-10-30 00:00:00")]); db.commit(); db.close()

def test_import_is_read_only_idempotent_and_count_matches(tmp_path):
    source=tmp_path/"tasks.db"; target=tmp_path/"new.db"; report=tmp_path/"report.json"; make_legacy(source)
    url=f"sqlite:///{target.as_posix()}"; engine=create_engine(url); Base.metadata.create_all(engine)
    first=import_legacy(source,url,report); second=import_legacy(source,url,report)
    assert first["source_count"]==first["imported"]==2
    assert second["imported"]==0 and second["skipped_existing"]==2
    assert Path(first["backup"]).exists() and source.exists() and report.exists()
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Task))==2
        assert db.scalar(select(Task).where(Task.legacy_source_id==2)).status=="done"
