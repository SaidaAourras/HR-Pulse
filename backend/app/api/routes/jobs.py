import json
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.api.db.database import get_db
from backend.app.api.db.models.job import JobModel
from backend.app.api.db.schemas.job import JobResponse
from sqlalchemy import cast, String

# Import de la validation JWT (ajuste le chemin si nécessaire)
from backend.app.services.auth_services import verify_token

job_router = APIRouter(prefix="/jobs" , tags=["Jobs"])

@job_router.get("/", response_model=list[JobResponse])
def list_jobs(
    page : int = Query(1,  ge=1),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    offset = (page - 1) * limit
    return db.query(JobModel).order_by(JobModel.id).limit(limit).offset(offset).all()


@job_router.get("/search/", response_model=list[JobResponse])
def search_jobs(
    skill: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token) # Ajout JWT
):
    results = db.query(JobModel).filter(
        cast(JobModel.skills_extracted, String).ilike(f"%{skill}%")
    ).all()
    if not results:
        raise HTTPException(404, detail=f"Aucune offre pour : {skill}")
    return results

@job_router.get("/skills/top/")
def top_skills(
    n: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token) # Ajout JWT
):
    jobs = db.query(JobModel.skills_extracted).all()
    all_skills = [
        s for (skills,) in jobs
        if skills
        for s in (skills if isinstance(skills, list) else json.loads(skills))
    ]
    top = Counter(all_skills).most_common(n)
    return {"top_skills": [{"skill": s, "count": c} for s, c in top]}


@job_router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token) # Ajout JWT
):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(404, detail=f"Job {job_id} introuvable")
    return job
