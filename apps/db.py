from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, echo=True)

SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_session():
    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

session_scope = contextmanager(get_session)