import pytest
from pathlib import Path
from gris import read_ris
import tempfile


# Get all RIS files in the tests/files directory
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
