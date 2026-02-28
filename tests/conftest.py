import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from backend.app.api.db.database import Base, get_db
from backend.app.services.auth_services import create_token

TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionTest = sessionmaker(bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine_test)
    db = SessionTest()
    from backend.app.api.db.models.job import JobModel
    jobs = [
        JobModel(id=1, job_title="Data Scientist",            skills_extracted=["Python", "SQL", "AWS"]),
        JobModel(id=2, job_title="Senior Data Scientist",     skills_extracted=["Python", "PyTorch", "Azure"]),
        JobModel(id=3, job_title="Machine Learning Engineer", skills_extracted=["Python", "Spark", "Docker"]),
    ]
    db.add_all(jobs)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def auth_headers():
    """Token JWT de test — meme payload que /auth/login."""
    token = create_token({"sub": "1", "email": "test@test.com"})
    return {"Authorization": f"Bearer {token}"}
