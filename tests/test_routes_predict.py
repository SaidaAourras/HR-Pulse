"""
Tests unitaires — Route Predict
"""

VALID_PAYLOAD = {
    "job_title"        : "Senior Data Scientist",
    "job_description"  : "We need a senior data scientist with Python, SQL, Azure and machine learning experience.",
    "sector"           : "Information Technology",
    "size"             : "51 to 200 employees",
    "type_of_ownership": "Company - Private",
    "state"            : "CA",
}


def test_predict_returns_200(client):
    r = client.post("/predict/", json=VALID_PAYLOAD)
    assert r.status_code == 200


def test_predict_response_fields(client):
    r = client.post("/predict/", json=VALID_PAYLOAD)
    data = r.json()
    assert "predicted_salary_k" in data
    assert "mae_k"              in data
    assert "salary_mean_k"      in data
    assert "salary_min_k"       in data
    assert "salary_max_k"       in data


def test_predict_salary_is_numeric(client):
    r = client.post("/predict/", json=VALID_PAYLOAD)
    data = r.json()
    assert isinstance(data["predicted_salary_k"], float)
    assert data["predicted_salary_k"] > 0


def test_predict_salary_in_range(client):
    r = client.post("/predict/", json=VALID_PAYLOAD)
    data = r.json()
    assert data["salary_min_k"] <= data["predicted_salary_k"] <= data["salary_max_k"]


def test_predict_missing_field(client):
    payload = VALID_PAYLOAD.copy()
    del payload["sector"]
    r = client.post("/predict/", json=payload)
    assert r.status_code == 422


def test_predict_unknown_sector(client):
    payload = VALID_PAYLOAD.copy()
    payload["sector"] = "Unknown Sector XYZ"
    r = client.post("/predict/", json=payload)
    # Doit quand meme repondre (OrdinalEncoder gere unknown_value=-1)
    assert r.status_code == 200