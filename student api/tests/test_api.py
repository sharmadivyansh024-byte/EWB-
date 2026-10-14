import os
import tempfile
os.environ["STUDENTS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
from fastapi.testclient import TestClient  
from app.main import app 
VALID = {"name": "Test User", "date_of_birth": "2004-01-01", "email": "t@example.com", "course": "Python"}
def test_full_crud_flow():
    with TestClient(app) as c:
        r = c.post("/students", json=VALID)
        assert r.status_code == 201
        sid = r.json()["id"]
        assert c.get(f"/students/{sid}").json()["name"] == "Test User"
        assert len(c.get("/students").json()) == 1
        assert len(c.get("/students?course=python").json()) == 1
        assert c.get("/students?born_after=2005-01-01").json() == []
        r = c.patch(f"/students/{sid}", json={"course": "Data Science"})
        assert r.status_code == 200 and r.json()["course"] == "Data Science"
        assert r.json()["name"] == "Test User"  # untouched fields preserved
        assert c.delete(f"/students/{sid}").status_code == 204
        assert c.get(f"/students/{sid}").status_code == 404
def test_validation_and_errors():
    with TestClient(app) as c:
        assert c.post("/students", json={**VALID, "email": "bad"}).status_code == 422
        assert c.post("/students", json={"name": "X", "date_of_birth": "2004-01-01"}).status_code == 422  # no contact
        assert c.post("/students", json={**VALID, "date_of_birth": "2999-01-01"}).status_code == 422
        assert c.get("/students/9999").status_code == 404
        assert c.delete("/students/9999").status_code == 404
        assert c.put("/students/9999", json={"name": "Z"}).status_code == 404
def test_duplicate_email():
    with TestClient(app) as c:
        c.post("/students", json={**VALID, "email": "dup@example.com"})
        assert c.post("/students", json={**VALID, "email": "dup@example.com"}).status_code == 409
