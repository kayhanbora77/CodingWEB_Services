from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    print(f"\nAPI Response: {json_response}")
    assert json_response == {"message": "Hello World"}
