import pytest
from pathlib import Path
from gris import read_ris, write_ris


TEST_FILES_DIR = Path(__file__).parent / "files"


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


@pytest.fixture
def sample_entries():
    return read_ris(str(ENCODING_DIR / "utf8.ris"))


def test_write_ris_has_no_bom(tmp_path, sample_entries):
    """Written files are not prefixed with a UTF-8 BOM."""
    out = tmp_path / "out.ris"
    write_ris(str(out), sample_entries)
    assert not out.read_bytes().startswith(b"\xef\xbb\xbf")


@pytest.mark.parametrize("native", [False, True])
def test_write_ris_round_trip_non_ascii(tmp_path, sample_entries, native):
    """Writing and reading back preserves non-ASCII text for both newline
    options."""
    out = tmp_path / "out.ris"
    write_ris(str(out), sample_entries, native_newlines=native)
    assert read_ris(str(out)) == sample_entries
