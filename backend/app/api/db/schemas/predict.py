from pydantic import BaseModel

class PredictRequest(BaseModel):
    job_title         : str
    job_description   : str
    sector            : str
    size              : str
    type_of_ownership : str
    state             : str

class PredictResponse(BaseModel):
    predicted_salary_k : float
    mae_k              : float
    salary_mean_k      : float
    salary_min_k       : float
    salary_max_k       : float
