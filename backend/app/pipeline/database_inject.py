import json
import sys
import os
import re
import pandas as pd
from sqlalchemy.orm import Session
sys.path.insert(0, os.getcwd())
from backend.app.api.db.database import engine, Base
from backend.app.api.db.models.job import JobModel


def normalize_title(title: str) -> str:
    title = str(title).strip()
    replacements = {
        r'\bSr\.?\b': 'Senior',
        r'\bJr\.?\b': 'Junior',
        r'\bML\b':    'Machine Learning',
        r'\bDS\b':    'Data Science',
    }
    for pattern, repl in replacements.items():
        title = re.sub(pattern, repl, title, flags=re.IGNORECASE)
    return title.strip()


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Table 'jobs' creee.")


def inject(csv_path: str):
    df = pd.read_csv(csv_path)

    with Session(engine) as session:
        for _, row in df.iterrows():
            try:
                skills = json.loads(row["skills_extracted"]) if pd.notna(row["skills_extracted"]) else []
            except (json.JSONDecodeError, TypeError):
                skills = []

            job_title = normalize_title(row["job_title_clean"])
            job       = session.get(JobModel, int(row["id"]))

            if job:
                job.job_title        = job_title
                job.skills_extracted = skills
            else:
                session.add(JobModel(
                    id               = int(row["id"]),
                    job_title        = job_title,
                    skills_extracted = skills,
                ))
        session.commit()
    print(f"{len(df)} offres injectees.")


def check(n=5):
    with Session(engine) as session:
        jobs = session.query(JobModel).limit(n).all()
    for job in jobs:
        preview = job.skills_extracted[:3] if job.skills_extracted else []
        print(f"  [{job.id}] {job.job_title[:40]:<40} {preview}")


if __name__ == "__main__":
    csv = sys.argv[1] if len(sys.argv) > 1 else "data/ds-jobs-ner.csv"
    create_tables()
    inject(csv)
    print("Apercu :")
    check()
