from sqlalchemy.ext.declarative import declarative_base
from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from src.config import AppConfigs

Base = declarative_base()

engine = create_engine(AppConfigs.DB_CONNECTION_STRING, echo=False)

def session() -> Generator[Session, None, None]:

    dbsession: Session = scoped_session(
        sessionmaker(autoflush=False, autocommit=False, bind=engine)
    )()
    try:
        yield dbsession
    except Exception:
        dbsession.rollback()
        raise
    finally:
        dbsession.close()