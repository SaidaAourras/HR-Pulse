from pydantic import BaseModel
from typing import List, Optional

class JobBase(BaseModel):
    job_title: str
    skills_extracted: List[str] = []

class JobCreate(JobBase):
    id: int

class JobResponse(BaseModel):
    id               : int
    job_title        : str
    skills_extracted : Optional[str] = None

    model_config = {"from_attributes": True}