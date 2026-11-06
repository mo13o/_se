"""Safely import Level 1 tasks.db without modifying it."""
import argparse, json, shutil, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from app.db.session import build_engine
from app.models.task import Task
from app.models.user import User
CATEGORY={"作業":"assignment","考試":"exam","專題":"project","其他":"other"}
PRIORITY={"高":"high","中":"medium","低":"low"}

def import_legacy(source: Path,database_url: str,report_path: Path,owner_email: str | None = None) -> dict:
    if not source.is_file(): raise FileNotFoundError(f"找不到舊資料庫：{source}")
    backup=source.with_name(f"{source.stem}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}{source.suffix}")
    shutil.copy2(source,backup)
    source_db=sqlite3.connect(f"file:{source.as_posix()}?mode=ro",uri=True); source_db.row_factory=sqlite3.Row
    columns={row[1] for row in source_db.execute("PRAGMA table_info(tasks)")}
    required={"id","title","category","due_date","priority","notes","completed","created_at"}
    if not required.issubset(columns): raise ValueError("舊資料庫 tasks 欄位不完整")
    rows=source_db.execute("SELECT * FROM tasks ORDER BY id").fetchall(); source_db.close()
    Session=sessionmaker(bind=build_engine(database_url),expire_on_commit=False)
    imported=skipped=0
    with Session.begin() as db:
        owner = db.scalar(select(User).where(User.email==owner_email.lower())) if owner_email else None
        if owner_email and not owner: raise ValueError("找不到指定匯入帳號")
        existing=set(db.scalars(select(Task.legacy_source_id).where(Task.legacy_source_id.is_not(None))))
        for row in rows:
            if row["id"] in existing: skipped+=1; continue
            created=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(timezone.utc)
            done=bool(row["completed"])
            db.add(Task(owner_id=owner.id if owner else None,title=row["title"].strip(),description=row["notes"] or "",category=CATEGORY.get(row["category"],"other"),priority=PRIORITY.get(row["priority"],"medium"),status="done" if done else "todo",due_date=datetime.fromisoformat(row["due_date"]).date(),created_at=created,updated_at=created,completed_at=created if done else None,legacy_source_id=row["id"]))
            imported+=1
    result={"source_count":len(rows),"imported":imported,"skipped_existing":skipped,"final_mapped_count":len(rows),"backup":str(backup)}
    report_path.parent.mkdir(parents=True,exist_ok=True); report_path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

def main():
    parser=argparse.ArgumentParser(description="Import TaskFlow Level 1 tasks")
    parser.add_argument("--legacy-db",required=True,type=Path); parser.add_argument("--owner-email",required=True); parser.add_argument("--database-url",required=True); parser.add_argument("--report",type=Path,default=Path("migration-report.json"))
    args=parser.parse_args(); print(json.dumps(import_legacy(args.legacy_db.resolve(),args.database_url,args.report.resolve(),args.owner_email),ensure_ascii=False,indent=2))
if __name__=="__main__": main()


