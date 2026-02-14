def test_storage_clients_import() -> None:
    from storage.cosmos import CosmosStore
    from storage.search import SearchStore

    assert CosmosStore is not None
    assert SearchStore is not None
