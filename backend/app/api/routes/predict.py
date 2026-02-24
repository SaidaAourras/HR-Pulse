import json
import pandas as pd
from fastapi import APIRouter, HTTPException
from backend.app.api.db.schemas.predict import PredictResponse , PredictRequest
from backend.app.services.predict_services import load_artifacts


predict_router = APIRouter(prefix="/predict" , tags=["Predict"])


@predict_router.post("/" , response_model=PredictResponse)
def predict_salary(req: PredictRequest):
    model , encoder , meta = load_artifacts()
    
    X = encoder.transform(pd.DataFrame([[req.sector, req.size, req.type_of_ownership, req.state]], columns=meta["cat_cols"])) 
    
    prediction = round(float(model.predict(X)[0]),1)
    
    return PredictResponse(
        predicted_salary_k = prediction,
        mae_k              = meta["mae_k"],
        salary_mean_k      = meta["salary_mean"],
        salary_min_k       = meta["salary_min"],
        salary_max_k       = meta["salary_max"],
        )






