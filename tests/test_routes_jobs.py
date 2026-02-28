"""Tests unitaires — Routes Jobs"""


def test_list_jobs(client, auth_headers):
    r = client.get("/jobs/", headers=auth_headers)
    assert r.status_code == 200


def test_list_jobs_pagination(client, auth_headers):
    r = client.get("/jobs/?page=1&limit=2", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) <= 2


def test_get_job_by_id(client, auth_headers):
    r = client.get("/jobs/1", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["id"]        == 1
    assert data["job_title"] == "Data Scientist"


def test_get_job_not_found(client, auth_headers):
    r = client.get("/jobs/9999", headers=auth_headers)
    assert r.status_code == 404


def test_search_jobs(client, auth_headers):
    r = client.get("/jobs/search/?skill=Python", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for job in data:
        assert "Python" in job["skills_extracted"]


def test_search_jobs_not_found(client, auth_headers):
    r = client.get("/jobs/search/?skill=XYZNOTEXIST", headers=auth_headers)
    assert r.status_code == 404




def test_top_skills(client, auth_headers):
    r = client.get("/jobs/skills/top/", headers=auth_headers)
    assert r.status_code == 200
