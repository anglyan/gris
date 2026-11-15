import pytest
from pathlib import Path
from gris import read_ris, write_ris
import os
import tempfile


# The list of all the RIS files in the tests/files directory
TEST_FILES_DIR = Path(__file__).parent / "files"
RIS_FILES = list(TEST_FILES_DIR.glob("*.ris"))

@pytest.mark.parametrize("ris_file", RIS_FILES, ids=[f.name for f in RIS_FILES])
def test_read_ris_files(ris_file):
    """Test that read_ris can successfully read each RIS file without failure."""
    # This test passes if read_ris doesn't raise an exception
    result = read_ris(str(ris_file))

    # Basic validation that we got a list back
    assert isinstance(result, list), f"read_ris should return a list for {ris_file.name}"

    # Optional: verify the result is not empty (comment out if empty files are valid)
    assert len(result) > 0, f"read_ris returned empty list for {ris_file.name}"


def test_read_ris_no_valid_content():
    """Test that read_ris raises an error when file contains no valid RIS content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ris', delete=False) as f:
        f.write("This is just some header text\n")
        f.write("With no valid RIS tags\n")
        f.write("\n")
        temp_path = f.name

    try:
        with pytest.raises(IOError, match="No valid RIS content found"):
            read_ris(temp_path)
    finally:
        Path(temp_path).unlink()


# Subset of tests working with truncated files

TRUNCATED = (
    "TY  - JOUR\nTI  - Complete\nER  - \n\n"
    "TY  - JOUR\nTI  - Truncated\nAU  - Doe, Jane\n"
)

@pytest.fixture
def truncated_file(tmp_path):
    path = tmp_path / "truncated.ris"
    path.write_text(TRUNCATED)
    return str(path)


def test_read_ris_truncated_warns_by_default(truncated_file):
    """A file that ends mid record warns and discards the partial record."""
    with pytest.warns(UserWarning, match="line 5"):
        result = read_ris(truncated_file)
    assert [r["TI"] for r in result] == ["Complete"]


def test_read_ris_truncated_allowed_warns(truncated_file):
    with pytest.warns(UserWarning, match="missing end of record"):
        result = read_ris(truncated_file, allow_truncated=True)
    assert len(result) == 1


def test_read_ris_truncated_not_allowed_raises(truncated_file):
    with pytest.raises(IOError, match="line 5"):
        read_ris(truncated_file, allow_truncated=False)


def test_read_ris_complete_file_does_not_warn(tmp_path):
    """A well formed file does not warn, whatever the flag."""
    import warnings
    path = tmp_path / "ok.ris"
    path.write_text("TY  - JOUR\nTI  - Complete\nER  - \n")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert len(read_ris(str(path))) == 1
        assert len(read_ris(str(path), allow_truncated=False)) == 1

