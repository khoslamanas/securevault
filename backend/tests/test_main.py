import os

os.environ["DATABASE_URL"] = "postgresql+psycopg2://localhost/securevault_test"
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
def test_login_with_invalid_credentials():
    response = client.post(
        "/api/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
def test_invalid_jwt_token():
    response = client.get(
        "/api/me",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
def test_user_cannot_delete_another_users_entry(test_db):
    from app.database import SessionLocal
    from app.models import User, VaultEntry

    db = test_db
    connection = db.connection()
    transaction = connection.begin_nested()
    from app.main import get_db

def override_get_db():
    yield db

    app.dependency_overrides[get_db] = override_get_db

    owner = User(
        email="vault_owner_test@example.com",
        hashed_password="test_hash"
    )

    other_user = User(
        email="vault_other_test@example.com",
        hashed_password="test_hash"
    )

    try:
        # Create two separate test users.
        db.add_all([owner, other_user])
        db.flush()

        # Create a password belonging to the first user.
        entry = VaultEntry(
            user_id=owner.id,
            website="example.com",
            username="testuser",
            encrypted_password="test_encrypted_value"
        )

        db.add(entry)
        db.flush()

        entry_id = entry.id

        # Authenticate as the second user.
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": str(other_user.id),
            "email": other_user.email
        }

        # Attempt to delete the first user's entry.
        response = client.delete(f"/api/vault/{entry_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Vault entry not found"

    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)

    db.rollback()
    db.close()

def test_duplicate_email_registration(test_db):
    from app.models import User
    from app.security import hash_password

    existing_user = User(
        email="duplicate_test@example.com",
        hashed_password=hash_password("TestPassword123!")
    )

    test_db.add(existing_user)
    test_db.flush()

    response = client.post(
        "/api/register",
        json={
            "email": "duplicate_test@example.com",
            "password": "AnotherPassword123!"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_successful_registration(test_db):
    from app.models import User

    response = client.post(
        "/api/register",
        json={
            "email": "new_registration_test@example.com",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200

    user = test_db.query(User).filter(
        User.email == "new_registration_test@example.com"
    ).first()

    assert user is not None
    assert user.hashed_password != "TestPassword123!"
def test_password_hashing():
    from app.security import hash_password, verify_password

    password = "SecureTest123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False

def test_password_encryption():
    from app.security import encrypt_password, decrypt_password

    original_password = "SecureVaultTest123!"

    encrypted = encrypt_password(original_password)
    decrypted = decrypt_password(encrypted)

    # The encrypted password must differ from the original.
    assert encrypted != original_password

    # Decryption must recover the original password.
    assert decrypted == original_password

    # Encrypting the same password twice should produce
    # different encrypted values.
    encrypted_again = encrypt_password(original_password)
    assert encrypted != encrypted_again