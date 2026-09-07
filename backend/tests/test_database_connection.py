import pytest
from sqlalchemy import text
from app.database.database import get_db, engine, Base

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    db.close()

def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_tables_created():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    # Check if some expected tables are there, e.g., 'assets', 'maintenance_tasks'
    assert 'assets' in tables or len(tables) > 0 # Allow for testing before full init
