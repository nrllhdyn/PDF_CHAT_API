import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_pdf():
    with open("tests/test_files/sample.pdf", "rb") as pdf_file:
        response = client.post(
            "/api/v1/pdf/upload",
            files={"file": ("sample.pdf", pdf_file, "application/pdf")}
        )
    assert response.status_code == 200
    assert "id" in response.json()

def test_list_pdfs():
    response = client.get("/api/v1/pdf/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.parametrize("endpoint", [
    "/api/v1/pdf/upload",
    "/api/v1/pdf/list",
    "/api/v1/chat/some_id/chat"
])
def test_rate_limiting(endpoint):
    for _ in range(101):  # Rate limit is set to 100
        response = client.get(endpoint)
    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}