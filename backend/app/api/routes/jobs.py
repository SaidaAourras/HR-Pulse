import json
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.api.db.database import get_db
from backend.app.api.db.models.job import JobModel
from backend.app.api.db.schemas.job import JobResponse

job_router = APIRouter(prefix="/jobs" , tags=["Jobs"])

@job_router.get("/", response_model=list[JobResponse])
def list_jobs(page:int , limit:int , db: Session = Depends(get_db),):
    offset = (page - 1) * limit
    return db.query(JobModel).offset(offset).limit(limit).all()

