import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from backend.app.api.db.database import engine, Base
from backend.app.api.routes.jobs import job_router
from backend.app.api.routes.predict import predict_router
from backend.app.api.routes.auth import auth_router


def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Base de donnees prete.")
            return
        except OperationalError:
            print(f"Attente... ({retries} essais restants)")
            retries -= 1
            time.sleep(10)


app = FastAPI(title="HR-Pulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth_router)
app.include_router(job_router)
app.include_router(predict_router)


@app.get("/")
def root():
    return {"status": "ok"}