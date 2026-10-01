from fastapi.testclient import TestClient
from app.main import app, get_current_user

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
def test_password_generator_requires_login():
    response = client.get("/api/generate-password")

    assert response.status_code == 401
def test_password_generator_rejects_invalid_length():
    response = client.get(
        "/api/generate-password?length=5"
    )

    assert response.status_code == 401
from app.main import get_current_user


def test_password_generator_invalid_length():
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "1",
        "email": "test@example.com"
    }

    try:
        response = client.get(
            "/api/generate-password?length=5"
        )

        assert response.status_code == 400

    finally:
        app.dependency_overrides.clear()
def test_generated_password_strength():
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "1",
        "email": "test@example.com"
    }

    try:
        response = client.get(
            "/api/generate-password?length=20"
            "&include_numbers=true"
            "&include_symbols=true"
        )

        assert response.status_code == 200

        password = response.json()["password"]

        assert len(password) == 20
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*" for c in password)

    finally:
        app.dependency_overrides.clear()