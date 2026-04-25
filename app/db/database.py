from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import os
from .models import Base


def _db_path() -> Path:
    # Flet setzt FLET_APP_STORAGE_DATA auf iOS/Android auf den beschreibbaren App-Ordner
    storage = os.environ.get("FLET_APP_STORAGE_DATA")
    if storage:
        return Path(storage) / "data.db"
    return Path.home() / ".training_tracker" / "data.db"


def get_engine():
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", echo=False)


engine = get_engine()
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return SessionLocal()
