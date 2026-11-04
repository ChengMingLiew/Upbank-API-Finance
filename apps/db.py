from contextlib import contextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import settings

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

if __name__ == "__main__":

    with session_scope() as session:
        result = session.execute(select(1))
        print("Database connection OK:", result.scalar())