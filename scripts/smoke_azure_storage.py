from __future__ import annotations

import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config.settings import get_settings  # noqa: E402
from storage.cosmos import CosmosStore  # noqa: E402
from storage.search import SearchStore  # noqa: E402


def _missing_env(names: list[str]) -> list[str]:
    return [name for name in names if not os.getenv(name)]


def _run_cosmos_smoke() -> None:
    required = ["COSMOS_ENDPOINT", "COSMOS_KEY"]
    missing = _missing_env(required)
    if missing:
        print(f"COSMOS: SKIP missing env vars: {', '.join(missing)}")
        return

    store = CosmosStore()
    store.ensure_database_and_containers()

    threat_id = f"tf-smoke-{uuid.uuid4().hex}"
    document = {
        "id": threat_id,
        "source": "smoke",
        "type": "smoke-test",
        "title": "Delvn smoke threat",
        "raw": {"kind": "smoke"},
    }
    store.upsert_threat(document)

    loaded = store.get_threat(threat_id, document["source"])
    assert loaded is not None, "COSMOS: read-back returned no document"
    assert loaded.get("id") == threat_id, "COSMOS: read-back id mismatch"
    print("COSMOS: OK ensure + upsert + read")


def _run_search_smoke() -> None:
    required = ["SEARCH_ENDPOINT", "SEARCH_KEY"]
    missing = _missing_env(required)
    if missing:
        print(f"SEARCH: SKIP missing env vars: {', '.join(missing)}")
        return

    settings = get_settings()
    store = SearchStore(settings=settings)
    index_name = settings.SEARCH_INDEX_THREATS
    embedding_dim = settings.EMBEDDING_DIM
    store.ensure_index(index_name, embedding_dim=embedding_dim)

    doc_id = f"tf-smoke-{uuid.uuid4().hex}"
    document = {
        "id": doc_id,
        "source": "smoke",
        "type": "smoke-test",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "content": "tf-smoke storage and search connectivity check",
        "contentVector": [0.0] * embedding_dim,
    }
    store.upsert_documents([document], index_name=index_name)

    found = False
    for _ in range(10):
        results = store.search_text("tf-smoke", top=5, index_name=index_name)
        if any(item.get("id") == doc_id for item in results):
            found = True
            break
        time.sleep(1)

    assert found, "SEARCH: upserted document not found by text query"
    print("SEARCH: OK ensure_index + upsert + search")


def _run_foundry_embedding_smoke() -> None:
    required = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION",
    ]
    missing = _missing_env(required)
    if missing:
        print(f"FOUNDRY: SKIP missing env vars: {', '.join(missing)}")
        return

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    deployment = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    api_version = os.environ["AZURE_OPENAI_API_VERSION"]
    url = f"{endpoint}/openai/deployments/{deployment}/embeddings"

    response = httpx.post(
        url,
        params={"api-version": api_version},
        headers={
            "api-key": os.environ["AZURE_OPENAI_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"input": "tf-smoke"},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    data = payload.get("data")
    assert isinstance(data, list) and data, "FOUNDRY: response missing data"
    embedding = data[0].get("embedding")
    assert isinstance(embedding, list) and embedding, (
        "FOUNDRY: invalid embedding response"
    )
    print("FOUNDRY: OK embeddings response shape")


def main() -> int:
    _run_cosmos_smoke()
    _run_search_smoke()
    _run_foundry_embedding_smoke()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
