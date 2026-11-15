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


TRUNCATED = (
    "TY  - JOUR\nTI  - Complete\nER  - \n\n"
    "TY  - JOUR\nTI  - Truncated\nAU  - Doe, Jane\n"
)


@pytest.fixture
def truncated_file(tmp_path):
    path = tmp_path / "truncated.ris"
    path.write_text(TRUNCATED, encoding="utf-8")
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
    path.write_text("TY  - JOUR\nTI  - Complete\nER  - \n", encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert len(read_ris(str(path))) == 1
        assert len(read_ris(str(path), allow_truncated=False)) == 1


LEGACY = "TY  - JOUR\nTI  - Café au lait\nAU  - Müller, Hans\nER  - \n"


def test_read_ris_plain_ascii(tmp_path):
    """Pure ASCII files, with either line ending, are read by default."""
    for eol in ("\n", "\r\n", "\r"):
        path = tmp_path / "ascii.ris"
        path.write_bytes(
            f"TY  - JOUR{eol}TI  - Plain title{eol}ER  - {eol}".encode("ascii"))
        result = read_ris(str(path))
        assert [r["TI"] for r in result] == ["Plain title"]


@pytest.mark.parametrize("encoding", ["cp1252", "latin-1"])
def test_read_ris_legacy_encoding(tmp_path, encoding):
    """Files in a legacy 8-bit encoding can be read with encoding=."""
    path = tmp_path / "legacy.ris"
    path.write_bytes(LEGACY.encode(encoding))
    result = read_ris(str(path), encoding=encoding)
    assert result[0]["TI"] == "Café au lait"
    assert result[0]["AU"] == "Müller, Hans"


def test_read_ris_legacy_encoding_default_raises(tmp_path):
    """Without encoding=, a non UTF-8 file raises instead of being garbled."""
    path = tmp_path / "legacy.ris"
    path.write_bytes(LEGACY.encode("cp1252"))
    with pytest.raises(UnicodeDecodeError):
        read_ris(str(path))


ENCODING_DIR = TEST_FILES_DIR / "encodings"

# file name -> (encoding argument, expected title)
ENCODED_FILES = {
    "ascii.ris": ("utf-8-sig", "Cafe au lait and Angstrom units"),
    "utf8.ris": ("utf-8-sig", "Café au lait and Ångström units"),
    "utf8_bom.ris": ("utf-8-sig", "Café au lait and Ångström units"),
    "utf16.ris": ("utf-16", "Café au lait and Ångström units"),
    "latin1.ris": ("latin-1", "Café au lait and Ångström units"),
    "cp1252.ris": ("cp1252", "“Café” – a study"),
    "mac_roman.ris": ("mac_roman", "Café au lait and Ångström units"),
    "cp850.ris": ("cp850", "Café au lait and Ångström units"),
}


@pytest.mark.parametrize("name", ENCODED_FILES)
def test_read_ris_encoded_files(name):
    """Each sample file is read correctly with its matching encoding."""
    encoding, title = ENCODED_FILES[name]
    result = read_ris(str(ENCODING_DIR / name), encoding=encoding)
    assert len(result) == 1
    assert result[0]["TI"] == title
    assert result[0]["JO"] == "Rev. Fr. Chim."


@pytest.mark.parametrize("name", ["ascii.ris", "utf8.ris", "utf8_bom.ris"])
def test_read_ris_encoded_files_default(name):
    """ASCII and UTF-8 files, with or without BOM, need no encoding."""
    _, title = ENCODED_FILES[name]
    assert read_ris(str(ENCODING_DIR / name))[0]["TI"] == title


@pytest.mark.parametrize("name", ["utf16.ris", "cp1252.ris", "cp850.ris"])
def test_read_ris_encoded_files_default_raises(name):
    """Files that are not UTF-8 raise with the default encoding."""
    with pytest.raises(UnicodeDecodeError):
        read_ris(str(ENCODING_DIR / name))


def test_read_ris_wrong_encoding_is_silent():
    """Latin-1 decodes any byte, so a wrong choice does not raise but gives
    wrong text, which is why gris does not guess the encoding."""
    wrong = read_ris(str(ENCODING_DIR / "mac_roman.ris"), encoding="latin-1")
    assert wrong[0]["TI"] != ENCODED_FILES["mac_roman.ris"][1]
