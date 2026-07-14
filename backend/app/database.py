import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_PATH = os.environ.get("TIPS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "tips.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_light_migrations():
    """SQLite has no ALTER-based migration tool wired up yet, so newly added
    columns are patched in directly. Safe to call every startup - each ADD
    COLUMN is wrapped so an already-migrated DB just no-ops."""
    with engine.connect() as conn:
        existing_cols = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(opportunities)")}
        if "is_rolling" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE opportunities ADD COLUMN is_rolling BOOLEAN DEFAULT 0")
        if "dilution_type" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE opportunities ADD COLUMN dilution_type VARCHAR")
        if "tier" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE opportunities ADD COLUMN tier VARCHAR")
        if "domain" not in existing_cols:
            conn.exec_driver_sql("ALTER TABLE opportunities ADD COLUMN domain VARCHAR")
        conn.commit()
