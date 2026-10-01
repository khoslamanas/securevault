import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://localhost/securevault_test"
)

import pytest
from sqlalchemy.orm import Session

from app.database import engine
from app.main import app, get_db


@pytest.fixture
def test_db():
    connection = engine.connect()
    transaction = connection.begin()

    db = Session(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield db
    finally:
        app.dependency_overrides.pop(get_db, None)
        db.close()
        transaction.rollback()
        connection.close()