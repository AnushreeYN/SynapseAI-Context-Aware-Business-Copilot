from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient


def test_auth_document_dashboard_flow() -> None:
    email = "flow@example.com"
    password = "strong-password"

    with TestClient(app) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Flow Tester"},
        )
        assert register_response.status_code in {201, 409}

        login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == email

        sample_path = Path("samples/sample_invoice.csv")
        with sample_path.open("rb") as handle:
            upload_response = client.post(
                "/api/v1/documents/upload",
                headers=headers,
                files={"file": ("sample_invoice.csv", handle, "text/csv")},
            )
        assert upload_response.status_code == 201
        document = upload_response.json()["document"]
        document_id = document["id"]
        assert document["status"] == "processed"

        list_response = client.get("/api/v1/documents", headers=headers)
        assert list_response.status_code == 200
        assert any(item["id"] == document_id for item in list_response.json())

        detail_response = client.get(f"/api/v1/documents/{document_id}", headers=headers)
        assert detail_response.status_code == 200
        assert "INV-2026-104" in detail_response.json()["extracted_text_preview"]

        patch_response = client.patch(
            f"/api/v1/documents/{document_id}",
            headers=headers,
            json={"original_filename": "renamed_invoice.csv"},
        )
        assert patch_response.status_code == 200
        assert patch_response.json()["original_filename"] == "renamed_invoice.csv"

        stats_response = client.get("/api/v1/dashboard/stats", headers=headers)
        assert stats_response.status_code == 200
        assert stats_response.json()["total_documents"] >= 1

        delete_response = client.delete(f"/api/v1/documents/{document_id}", headers=headers)
        assert delete_response.status_code == 204

        missing_response = client.get(f"/api/v1/documents/{document_id}", headers=headers)
        assert missing_response.status_code == 404
