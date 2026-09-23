from pathlib import Path

from app.data.provenance import dataset_fingerprint, input_identity


def test_input_identity_and_fingerprint_are_content_addressed(tmp_path: Path):
    source = tmp_path / "prices.csv"
    source.write_text("ticker,close\nAAA,10\n", encoding="utf-8")
    identity = input_identity(source)
    configuration = {"momentum_months": 3}

    first = dataset_fingerprint({"prices": identity}, configuration)
    second = dataset_fingerprint({"prices": identity}, configuration)

    assert len(identity["sha256"]) == 64
    assert first == second
    assert len(first) == 64

    source.write_text("ticker,close\nAAA,11\n", encoding="utf-8")
    changed = dataset_fingerprint({"prices": input_identity(source)}, configuration)
    assert changed != first
