from sqlalchemy import Column, Integer, String, JSON
from backend.app.api.db.database import Base


class JobModel(Base):
    __tablename__ = "jobs"

    id               = Column(Integer, primary_key=True, index=True)
    job_title        = Column(String(255), nullable=False)
    skills_extracted = Column(JSON,        nullable=True)