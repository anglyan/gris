import pytest
from gris import read_ris, write_ris
import os

@pytest.fixture
def sample_entries():
    return [
        {"TY": "JOUR", "TI": "A title", "AU": ["Doe, Jane", "Roe, Rick"]},
        {"TY": "BOOK", "TI": "Another title"},
    ]


def test_write_ris_default_uses_crlf(tmp_path, sample_entries):
    """By default lines end with CRLF on every platform."""
    out = tmp_path / "out.ris"
    write_ris(str(out), sample_entries)
    data = out.read_bytes()
    assert b"\r\n" in data
    assert data.replace(b"\r\n", b"").count(b"\n") == 0


def test_write_ris_native_newlines(tmp_path, sample_entries):
    """native_newlines=True uses the platform line separator."""
    out = tmp_path / "out.ris"
    write_ris(str(out), sample_entries, native_newlines=True)
    data = out.read_bytes()
    sep = os.linesep.encode()
    assert data.replace(sep, b"").count(b"\n") == 0
    assert sep in data


@pytest.mark.parametrize("native", [False, True])
def test_write_ris_round_trip(tmp_path, sample_entries, native):
    """Writing and reading back preserves the entries for both options."""
    out = tmp_path / "out.ris"
    write_ris(str(out), sample_entries, native_newlines=native)
    assert read_ris(str(out)) == sample_entries
