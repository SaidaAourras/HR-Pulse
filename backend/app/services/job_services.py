from sqlalchemy.orm import Session
from . import models, schemas

def get_job(db: Session, job_id: int):
    return db.query(models.JobModel).filter(models.JobModel.id == job_id).first()

def create_or_update_job(db: Session, job: schemas.JobCreate):
    db_job = get_job(db, job.id)
    if db_job:
        db_job.job_title = job.job_title
        db_job.skills_extracted = job.skills_extracted
    else:
        db_job = models.JobModel(**job.model_dump())
        db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job