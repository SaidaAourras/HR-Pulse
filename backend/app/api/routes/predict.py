from fastapi import APIRouter, HTTPException
from backend.app.api.db.schemas.predict import PredictRequest, PredictResponse
from backend.app.services.predict_services import predict

predict_router = APIRouter(prefix="/predict", tags=["Predict"])


@predict_router.post("/", response_model=PredictResponse)
def predict_salary(req: PredictRequest):
    try:
        result = predict(
            job_title         = req.job_title,
            job_description   = req.job_description,
            sector            = req.sector,
            size              = req.size,
            type_of_ownership = req.type_of_ownership,
            state             = req.state,
        )
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
