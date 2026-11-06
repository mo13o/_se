from pathlib import Path
from collections.abc import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import get_settings

def build_engine(database_url: str | None = None) -> Engine:
    url=database_url or get_settings().database_url
    if url.startswith("sqlite:///") and url != "sqlite:///:memory:": Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True,exist_ok=True)
    built=create_engine(url,connect_args={"check_same_thread":False} if url.startswith("sqlite") else {})
    if url.startswith("sqlite"):
        @event.listens_for(built,"connect")
        def enable_foreign_keys(connection,_record):
            cursor=connection.cursor(); cursor.execute("PRAGMA foreign_keys=ON"); cursor.close()
    return built
engine=build_engine(); SessionLocal=sessionmaker(bind=engine,expire_on_commit=False)
def get_db() -> Generator[Session,None,None]:
    db=SessionLocal()
    try: yield db
    finally: db.close()
def database_is_ready() -> bool:
    try:
        with engine.connect() as connection: connection.execute(text("SELECT 1"))
        return True
    except Exception: return False
