import pytest
from pathlib import Path
from gris import (
    read_ris, write_ris, get_authors, get_pubtype, get_title, get_journal,
    get_volume, get_issue, get_pubdate, get_pubyear, get_startpage,
    get_endpage, get_abstract, get_keywords, get_doi,
    remove_newlines,
)
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


@pytest.mark.parametrize("ris_file", RIS_FILES, ids=[f.name for f in RIS_FILES])
def test_all_references_have_authors(ris_file):
    """Every reference in every test file must return a non empty author list."""
    refs = read_ris(str(ris_file))
    assert refs, f"No references found in {ris_file.name}"
    for i, ref in enumerate(refs):
        authors = get_authors(ref)
        assert authors, f"Reference {i} in {ris_file.name} has no authors"
        assert all(a.strip() for a in authors), (
            f"Reference {i} in {ris_file.name} has an empty author name"
        )


# Helpers that return a string, 'NA' when the data is missing. These fields
# are expected in every reference of the test files.
REQUIRED_GETTERS = [
    get_pubtype, get_title, get_journal, get_volume,
    get_pubdate, get_pubyear, get_startpage,
]

# Fields that are legitimately absent from some references (no issue number
# in journals that only number volumes, no end page for article numbers, no
# abstract or keywords in many exports)
OPTIONAL_STRING_GETTERS = [get_issue, get_endpage, get_abstract]


def _all_refs():
    return [(f.name, i, ref) for f in RIS_FILES
            for i, ref in enumerate(read_ris(str(f)))]


ALL_REFS = _all_refs()
REF_IDS = [f"{name}[{i}]" for name, i, _ in ALL_REFS]


@pytest.mark.parametrize("getter", REQUIRED_GETTERS, ids=lambda g: g.__name__)
@pytest.mark.parametrize("ref", [r for _, _, r in ALL_REFS], ids=REF_IDS)
def test_required_getters_return_data(getter, ref):
    """Helpers for fields every reference has must not return empty or 'NA'."""
    value = getter(ref)
    assert isinstance(value, str)
    assert value.strip() not in ("", "NA"), f"{getter.__name__} returned {value!r}"


@pytest.mark.parametrize("getter", OPTIONAL_STRING_GETTERS, ids=lambda g: g.__name__)
@pytest.mark.parametrize("ref", [r for _, _, r in ALL_REFS], ids=REF_IDS)
def test_optional_getters_return_strings(getter, ref):
    """Optional fields return a string, 'NA' if missing, never an empty string."""
    value = getter(ref)
    assert isinstance(value, str)
    assert value.strip() != ""


@pytest.mark.parametrize("ref", [r for _, _, r in ALL_REFS], ids=REF_IDS)
def test_get_keywords_returns_list_of_nonempty_strings(ref):
    """Keywords may be absent ([]), but any keyword present must be non empty."""
    keywords = get_keywords(ref)
    assert isinstance(keywords, list)
    assert all(isinstance(k, str) and k.strip() for k in keywords)


def test_at_least_one_reference_has_each_optional_field():
    """Guards the optional tests above against passing on empty data."""
    refs = [r for _, _, r in ALL_REFS]
    assert any(get_issue(r) != "NA" for r in refs)
    assert any(get_endpage(r) != "NA" for r in refs)
    assert any(get_abstract(r) != "NA" for r in refs)
    assert any(get_keywords(r) for r in refs)


@pytest.mark.parametrize("text, expected", [
    ("Atomic\nLayer Deposition", "Atomic Layer Deposition"),
    ("Atomic\r\nLayer", "Atomic Layer"),
    ("Atomic \n Layer", "Atomic Layer"),
    ("Atomic\n\nLayer", "Atomic Layer"),
    ("  Atomic Layer\n", "Atomic Layer"),
    ("No line breaks here", "No line breaks here"),
    ("", ""),
    ("NA", "NA"),
])
def test_remove_newlines(text, expected):
    assert remove_newlines(text) == expected


def test_remove_newlines_on_acs_reference():
    """The ACS file wraps its title and abstract over several lines."""
    ref = read_ris(str(TEST_FILES_DIR / "acsNov26.ris"))[0]
    assert "\n" in get_title(ref)
    for getter in (get_title, get_abstract):
        assert "\n" not in remove_newlines(getter(ref))
    assert remove_newlines(get_title(ref)) == (
        "Intelligent Agents for the Optimization of Atomic Layer Deposition"
    )


@pytest.mark.parametrize("getter", [get_title, get_abstract, get_journal],
                         ids=lambda g: g.__name__)
@pytest.mark.parametrize("ref", [r for _, _, r in ALL_REFS], ids=REF_IDS)
def test_strip_newlines_flag(getter, ref):
    """strip_newlines=True removes line breaks, and the default keeps them."""
    raw = getter(ref)
    assert getter(ref, strip_newlines=False) == raw
    assert getter(ref, strip_newlines=True) == remove_newlines(raw)
    assert "\n" not in getter(ref, strip_newlines=True)


def test_strip_newlines_flag_on_acs_reference():
    ref = read_ris(str(TEST_FILES_DIR / "acsNov26.ris"))[0]
    assert "\n" in get_title(ref)
    assert "\n" in get_abstract(ref)
    assert get_title(ref, strip_newlines=True) == (
        "Intelligent Agents for the Optimization of Atomic Layer Deposition"
    )
    assert "\n" not in get_abstract(ref, strip_newlines=True)


def test_strip_newlines_flag_missing_field():
    """Missing data stays 'NA' when the flag is set."""
    assert get_title({}, strip_newlines=True) == "NA"
    assert get_abstract({}, strip_newlines=True) == "NA"
    assert get_journal({}, strip_newlines=True) == "NA"


# DOIs of the references in the test files, in the order they are read
EXPECTED_DOIS = {
    "NatureJan26.ris": ["10.1038/s43586-025-00435-6"],
    "aipJan26.ris": ["10.1116/6.0004319"],
    "acsNov26.ris": ["10.1021/acsami.1c00649"],
    "single_Zotero.ris": ["10.1016/j.jeurceramsoc.2015.08.028"],
    "multiple_Zotero.ris": ["10.1109/TBCAS.2014.2379294",
                            "10.1073/pnas.1106161108"],
}


@pytest.mark.parametrize("ris_file", RIS_FILES, ids=[f.name for f in RIS_FILES])
def test_get_doi_in_files(ris_file):
    """Every reference in the test files has a DOI, a bare string starting with 10."""
    dois = [get_doi(ref) for ref in read_ris(str(ris_file))]
    assert all(d.startswith("10.") for d in dois), dois
    if ris_file.name in EXPECTED_DOIS:
        assert dois == EXPECTED_DOIS[ris_file.name]


@pytest.mark.parametrize("ref, expected", [
    # DO tag, in the different ways it is written
    ({"DO": "10.1116/6.0004319"}, "10.1116/6.0004319"),
    ({"DO": "doi:10.1116/6.0004319"}, "10.1116/6.0004319"),
    ({"DO": "DOI: 10.1116/6.0004319"}, "10.1116/6.0004319"),
    ({"DO": "https://doi.org/10.1116/6.0004319"}, "10.1116/6.0004319"),
    ({"DO": " 10.1116/6.0004319 "}, "10.1116/6.0004319"),
    ({"DO": ["10.1116/6.0004319", "10.1000/other"]}, "10.1116/6.0004319"),
    # fall back to the URL when there is no DO tag
    ({"UR": "https://doi.org/10.1038/s43586-025-00435-6"},
     "10.1038/s43586-025-00435-6"),
    ({"UR": "http://dx.doi.org/10.1038/s43586-025-00435-6"},
     "10.1038/s43586-025-00435-6"),
    ({"UR": ["https://example.org/paper", "https://doi.org/10.1038/abc.1"]},
     "10.1038/abc.1"),
    ({"UR": "https://onlinelibrary.wiley.com/doi/abs/10.1002/adma.201801?af=R#top"},
     "10.1002/adma.201801"),
    ({"UR": "https://doi.org/10.1002%2Fadma.201801"}, "10.1002/adma.201801"),
    ({"L2": "https://doi.org/10.1002/adma.201801"}, "10.1002/adma.201801"),
    # balanced parentheses are part of the DOI, trailing punctuation is not
    ({"DO": "10.1002/(SICI)1097-4636(199801)39:1<1::AID-JBM1>3.0.CO;2-N"},
     "10.1002/(SICI)1097-4636(199801)39:1"),
    ({"UR": "(see https://doi.org/10.1038/abc.1)."}, "10.1038/abc.1"),
    ({"UR": "https://doi.org/10.1038/abc.1."}, "10.1038/abc.1"),
    # DO wins over UR
    ({"DO": "10.1116/6.0004319", "UR": "https://doi.org/10.1000/other"},
     "10.1116/6.0004319"),
    # a DO tag without a DOI does not hide the one in the URL
    ({"DO": "not available", "UR": "https://doi.org/10.1038/abc.1"},
     "10.1038/abc.1"),
])
def test_get_doi(ref, expected):
    assert get_doi(ref) == expected


@pytest.mark.parametrize("ref", [
    {},
    {"DO": ""},
    {"UR": "https://www.sciencedirect.com/science/article/pii/S0955221915301114"},
    {"UR": "https://example.org/10.12/not-a-doi"},
    {"TI": "10.1116/6.0004319"},  # only the DOI related tags are searched
])
def test_get_doi_missing(ref):
    assert get_doi(ref) == "NA"


def test_get_doi_from_url_only():
    """Removing DO from the references that have a doi.org URL still finds the DOI."""
    for name in ("NatureJan26.ris", "aipJan26.ris", "acsNov26.ris"):
        for ref in read_ris(str(TEST_FILES_DIR / name)):
            expected = get_doi(ref)
            ref = {k: v for k, v in ref.items() if k != "DO"}
            assert get_doi(ref) == expected
