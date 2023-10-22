import pytest
from fastapi.testclient import TestClient
from main import app, validate_montenegro_iban


client = TestClient(app)


def test_validate_montenegro_iban():
    assert validate_montenegro_iban('ME25505000012345678951') == True
    assert validate_montenegro_iban('ME21505000012345678952') == False


def test_validate_iban_endpoint():
    response = client.post(
        "/validate_iban/", json={"iban": "ME25505000012345678951"})
    assert response.status_code == 200
    assert response.json() == {"valid": True}


def test_realtime_validate_iban_endpoint():
    response = client.post("/realtime_validate_iban/",
                           json={"iban": "ME25505000012345678951"})
    assert response.status_code == 200
    assert response.json() == {
        "iban": "ME25505000012345678951", "valid_so_far": True}


def test_store_and_validate_iban_endpoint():
    response = client.post("/store_validate_iban/",
                           json={"iban": "ME25505000012345678951"})
    assert response.status_code == 200
    assert "timestamp" in response.json()
    assert response.json()["iban"] == "ME25505000012345678951"
    assert response.json()["valid"] == True


def test_get_validation_history():
    client.post("/store_validate_iban/",
                json={"iban": "ME25505000012345678951"})
    response = client.get("/get_validation_history/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_suggest_and_validate_iban_endpoint():
    response = client.post("/suggest_validate_iban/",
                           json={"iban": "MEa550b000c12345678951"})
    assert response.status_code == 200
    assert response.json()["suggested_iban"] == "ME455056000612345678951"
