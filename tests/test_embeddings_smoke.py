from __future__ import annotations

from config.settings import Settings
from embeddings.client import DeterministicHashEmbeddingClient, get_embedding_client


def test_hash_embedding_output_matches_configured_dimension() -> None:
    dimension = 32
    client = DeterministicHashEmbeddingClient(dim=dimension)

    vectors = client.embed(["alpha", "beta"])

    assert len(vectors) == 2
    assert all(len(vector) == dimension for vector in vectors)


def test_hash_embedding_is_deterministic_for_same_input() -> None:
    client = DeterministicHashEmbeddingClient(dim=24)

    first = client.embed(["same threat text"])[0]
    second = client.embed(["same threat text"])[0]
    different = client.embed(["different threat text"])[0]

    assert first == second
    assert first != different


def test_embedding_client_defaults_to_deterministic_fallback() -> None:
    settings = Settings(
        EMBEDDING_DIM=20,
        AZURE_OPENAI_ENDPOINT=None,
        AZURE_OPENAI_API_KEY=None,
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT=None,
    )

    client = get_embedding_client(settings)

    assert isinstance(client, DeterministicHashEmbeddingClient)
    assert len(client.embed(["fallback"])[0]) == 20
