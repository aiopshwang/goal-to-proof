from pathlib import Path

from importer import import_records


def test_writes_destination(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("id,effective_date,amount\nr-1,2026-01-01,1.00\n", encoding="utf-8")
    destination = tmp_path / "output.json"
    import_records(source, destination)
    assert destination.exists()
