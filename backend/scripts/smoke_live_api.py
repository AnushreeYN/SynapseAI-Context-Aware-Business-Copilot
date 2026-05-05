from pathlib import Path
import os
from time import time

import httpx


API_ROOT = os.getenv("SYNAPSE_API_ROOT", "http://127.0.0.1:8000")
BASE_URL = f"{API_ROOT}/api/v1"


def main() -> None:
    email = f"live-{int(time())}@synapse.ai"
    password = "strong-password"

    with httpx.Client(timeout=15.0) as client:
        health = client.get(f"{API_ROOT}/health")
        health.raise_for_status()

        register = client.post(
            f"{BASE_URL}/auth/register",
            json={"email": email, "password": password, "full_name": "Live Smoke Test"},
        )
        register.raise_for_status()

        login = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        me = client.get(f"{BASE_URL}/auth/me", headers=headers)
        me.raise_for_status()

        sample_path = Path("samples/sample_invoice.csv")
        with sample_path.open("rb") as handle:
            upload = client.post(
                f"{BASE_URL}/documents/upload",
                headers=headers,
                files={"file": ("sample_invoice.csv", handle, "text/csv")},
            )
        upload.raise_for_status()
        document_id = upload.json()["document"]["id"]

        documents = client.get(f"{BASE_URL}/documents", headers=headers)
        documents.raise_for_status()

        detail = client.get(f"{BASE_URL}/documents/{document_id}", headers=headers)
        detail.raise_for_status()

        rename = client.patch(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers,
            json={"original_filename": "live_renamed_invoice.csv"},
        )
        rename.raise_for_status()

        stats = client.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        stats.raise_for_status()

        delete = client.delete(f"{BASE_URL}/documents/{document_id}", headers=headers)
        delete.raise_for_status()

        missing = client.get(f"{BASE_URL}/documents/{document_id}", headers=headers)
        assert missing.status_code == 404

    print("Live API smoke test passed: auth, upload, list, detail, patch, stats, delete.")


if __name__ == "__main__":
    main()
