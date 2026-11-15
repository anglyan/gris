#Copyright (c) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

"""Methods to operate with the Refman RIS data format"""

import re
from urllib.parse import unquote

_missing_data = 'NA'
_journal_tags = ('JO', 'T2', 'JF', 'JA', 'J2', 'J1')
_pubdate_tags = ('DA', 'Y1', 'PY')
_pubyear_tags = ('PY', 'Y1', 'DA')
_year_pat = re.compile(r'(?<!\d)\d{4}(?!\d)')
_date_pat = re.compile(r'^\s*\d{4}\s*(?:/|$)')
_newline_pat = re.compile(r'\s*[\r\n]+\s*')
_doi_tags = ('DO', 'UR', 'L1', 'L2', 'L3', 'L4')
_doi_pat = re.compile(r'10\.\d{4,9}/[^\s"<>?#]+')

_ris_tags_ref = {
    'TY': "Type of reference - first tag",
    'A1': "Primary Authors - usually mapped to AU",
    'A2': "Secondary Authors - normally used for Editors",
    'A3': "Tertiary Authors",
    'A4': "Subsidiary Authors",
    'AB': "Notes - usually used for abstract and mapped to N2",
    'AD': "Author Address",
    'AN': "Accession Number",
    'AU': "Author",
    'AV': "Location in Archives",
    'BT': "This field maps to T2 except for Whole Book and Unpublished Work references",
    'C1': "Custom 1",
    'C2': "Custom 2",
    'C3': "Custom 3",
    'C4': "Custom 4",
    'C5': 'Custom 5',
    'C6': "Custom 6 - As of 2023 some references in WoS use this for Year + Month info",
    'C7': "Custom 7",
    'C8': 'Custom 8',
    'CA': "Caption",
    'CN': "Call Number",
    'CP': "Misc",
    'CT': "Title of unpublished reference",
    'CY': "Place Published",
    'DA': "Date",
    'DB': "Name of Database",
    'DO': "DOI",
    'DP': "Database Provider",
    'ED': "Editor",
    'EP': "End Page",
    'ET': "Edition",
    'ID': "Reference ID",
    'IS': "Issue number",
    'J1': "Periodical name: user abbreviation",
    'J2': "Alternate Title - Journal name for journals",
    'JA': "Periodical name: standard abbreviation",
    'JF': "Journal/Periodical name: full format",
    'JO': "Journal/Periodical name: full format",
    'KW': "Keywords",
    'L1': "Link to PDF",
    'L2': "Link to Full-text.",
    'L3': "Related Records",
    'L4': "Image(s)",
    'LA': "Language",
    'LB': "Label",
    'LK': "Website Link",
    'M1': "Number",
    'M2': "Miscellaneous 2",
    'M3': "Type of Work",
    'N1': "Notes",
    'N2': "Abstract",
    'NV': "Number of Volumes",
    'OP': "Original Publication",
    'PB': "Publisher",
    'PP': "Publishing Place",
    'PY': "Publication year",
    'RI': "Reviewed Item",
    'RN': "Research Notes",
    'RP': "Reprint Edition",
    'SE': "Section",
    'SN': "ISBN/ISSN",
    'SP': "Start Page",
    'ST': "Short Title",
    'T1': "Primary Title",
    'T2': "Secondary Title (journal title, if applicable)",
    'T3': "Title series",
    'TA': "Translated Author",
    'TI': "Title",
    'TT': "Translated Title",
    'U1': "User definable 1",
    'U3': "User definable 3",
    'U4': "User definable 4",
    'U5': "User definable 5",
    'UR': "URL",
    'VL': "Volume number",
    'VO': "Published Standard number",
    'Y1': "Primary Date",
    'Y2': "Access Date",
    'ER': "End of Reference"
}

_standard_ris_tags = {'TY', 'AU', 'A1', 'A2', 'A3', 'A4', 'AB', 'AD', 'AN', 'AV',
    'BT', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'CA', 'CN', 'CP',
    'CT', 'CY', 'DA', 'DB', 'DO', 'DP', 'ED', 'EP', 'ET', 'ID', 'IS', 'J1',
    'J2', 'JA', 'JF', 'JO', 'KW', 'L1', 'L2', 'L3', 'L4', 'LA', 'LB', 'LK',
    'M1', 'M2', 'M3', 'N1', 'N2', 'NV', 'OP', 'PB', 'PP', 'PY', 'RI', 'RN',
    'RP', 'SE', 'SN', 'SP', 'ST', 'T1', 'T2', 'T3', 'TA', 'TI', 'TT', 'U1',
    'U3', 'U4', 'U5', 'UR', 'VL', 'VO', 'Y1', 'Y2', 'ER'}

_standard_ris_types = {
    "ABST", "ADVS", "ART", "BILL", "BOOK", "CASE", "CHAP", "COMP", 
    "CONF", "CTLG", "DATA", "ELEC", "GEN", "HEAR", "ICOMM", "INPR", "JFULL",
    "JOUR", "MAP", "MGZN", "MPCT", "MUSIC", "NEWS", "PAMP", "PAT", "PCOMM", "RPRT",
    "SER", "SLIDE", "SOUND", "STAT", "THES", "UNBILL", "UNPB", "VIDEO"}

# Types found in later revisions of the RIS format and in files from other
# tools. They are not part of the original Refman specification.
_extended_ris_types = {"CLSWK", "CPAPER", "EBOOK", "ECHAP", "EJOUR"}

# Types written by Zotero's RIS export that are not part of the original
# Refman specification (see the RIS translator in github.com/zotero/translators).
# Zotero also exports types from the standard set above, such as THES and RPRT.
_zotero_ris_types = {"BLOG", "DICT", "ENCYC", "MANSCPT"}

_bibtext_ris_types = {
    "BOOK", "CHAP", "CLSWK", "CONF", "CPAPER", "EBOOK", "ECHAP", "EJOUR",
    "ELEC", "GEN", "JOUR", "MGZN", "RPRT", "SER", "THES", "UNPB"
}


def check_conforms(ref, zotero=False):
    """Check if a given reference conforms to the RIS standard

    Args:
        ref (dict) : a reference as returned by read_ris
        zotero (:obj:`bool`, optional) : if True, also accept the
            publication types that Zotero exports but that are not part of
            the original specification. Defaults False.
    """
    standard_keys = all(k.upper() in _standard_ris_tags for k in ref.keys())
    pubtype = get_pubtype(ref)
    valid_types = _standard_ris_types | _extended_ris_types
    if zotero:
        valid_types = valid_types | _zotero_ris_types
    return standard_keys and pubtype in valid_types

def get_pubtype(ref):
    """Return the publication type"""
    return tag2string(ref, 'TY')


def get_title(ref, strip_newlines=False):
    """Return the publication title, 'NA' if not present

    TI is used if present, otherwise T1 (the primary title, which is what
    sources such as AIP and ACS write).

    Args:
        ref (dict) : a reference as returned by read_ris
        strip_newlines (:obj:`bool`, optional) : if True, line breaks
            embedded in the title are replaced by spaces (see
            remove_newlines). Defaults False.
    """
    if 'TI' in ref:
        value = tag2string(ref, 'TI')
    else:
        value = tag2string(ref, 'T1')
    return _maybe_strip_newlines(value, strip_newlines)


def get_authors(ref):
    """Return a list of the authors"""
    if 'AU' in ref:
        return tag2list(ref, 'AU')
    else:
        return tag2list(ref, 'A1')


def get_journal(ref, strip_newlines=False):
    """Return the journal, 'NA' if not present

    Tags are tried in order of preference: JO, T2, JF, and then, as a last
    resort, the abbreviated names JA, J2 and J1. Zotero writes the journal
    title in T2 and the abbreviation in J2.

    Args:
        ref (dict) : a reference as returned by read_ris
        strip_newlines (:obj:`bool`, optional) : if True, line breaks
            embedded in the journal name are replaced by spaces (see
            remove_newlines). Defaults False.
    """
    for tag in _journal_tags:
        value = tag2string(ref, tag)
        if value != _missing_data:
            return _maybe_strip_newlines(value, strip_newlines)
    return _missing_data


def _extract_doi(text):
    """Return the first DOI found in text, None if there is none"""
    match = _doi_pat.search(unquote(text))
    if not match:
        return None
    doi = match.group(0).rstrip('.,;:')
    while doi.endswith(')') and doi.count(')') > doi.count('('):
        doi = doi[:-1].rstrip('.,;:')
    return doi


def get_doi(ref):
    """Return the DOI as a bare string such as '10.1021/acsami.1c00649',
    'NA' if it cannot be found.

    The DOI tag, DO, is tried first, followed by the tags that can contain
    a link to the publication: UR, L1, L2, L3 and L4. Many sources
    write the DOI as a URL, for instance 'https://doi.org/10.1021/acsami.1c00649',
    or with a 'doi:' prefix, and in the DO tag as well as in UR, so
    the DOI is extracted from the text in all cases. URL encoded characters
    are decoded, and query strings and fragments are discarded.
    """
    for tag in _doi_tags:
        for value in tag2list(ref, tag):
            doi = _extract_doi(value)
            if doi:
                return doi
    return _missing_data


def get_volume(ref):
    """Return the publication volume"""
    return tag2string(ref, 'VL')


def get_issue(ref):
    """Return the publication issue"""
    return tag2string(ref, 'IS')


def _first_dated_tag(ref, tags):
    """Return the content of the first tag in tags that contains a year,
    'NA' if there is none"""
    for tag in tags:
        value = tag2string(ref, tag).strip()
        if _year_pat.search(value):
            return value
    return _missing_data


def get_pubdate(ref):
    """Return the raw publication date string, 'NA' if not present.

    Tags are tried in order of level of detail: DA, Y1 and PY, so that the
    full date is returned when it is available. Zotero exports the
    full date in DA and only the year in PY. Use parse_pubyear to split
    the result into year, month, day and extra information.
    """
    return _first_dated_tag(ref, _pubdate_tags)


def get_pubyear(ref):
    """Return the four digit publication year as a string, 'NA' if it
    cannot be determined.

    The year is taken from the first of PY, Y1 and DA that contains one.
    """
    value = _first_dated_tag(ref, _pubyear_tags)
    match = _year_pat.search(value)
    return match.group(0) if match else _missing_data


def get_startpage(ref):
    """Return the start page and, if not present, the article number"""
    return tag2string(ref, 'SP')


def get_endpage(ref):
    """Return the end pager"""
    return tag2string(ref, 'EP')


def get_abstract(ref, strip_newlines=False):
    """Return the abstract

    Args:
        ref (dict) : a reference as returned by read_ris
        strip_newlines (:obj:`bool`, optional) : if True, line breaks
            embedded in the abstract are replaced by spaces (see
            remove_newlines). Defaults False.
    """
    if 'AB' in ref:
        value = tag2string(ref, 'AB')
    else:
        value = tag2string(ref, 'N2')
    return _maybe_strip_newlines(value, strip_newlines)


def get_keywords(ref):
    """Return a list of keywords"""
    if 'KW' in ref:
        return tag2list(ref, 'KW')
    else:
        return []


def parse_pubyear(v):
    """Parse a publication date field

    Dates in the RIS format are written as YYYY/MM/DD/extra info, where
    any of the fields can be empty. Zotero writes dates in this format
    when it can parse them, and the original free text otherwise (for
    instance "March 5, 2018"). In the latter case only the year is
    extracted.

    Returns:
        tuple : (year, month, day, extra). Fields that are empty or
        cannot be determined are None.
    """
    if _date_pat.match(v):
        chunks = [c.strip() or None for c in v.split('/', 3)]
        chunks += [None] * (4 - len(chunks))
        year, month, day, extra = chunks
        return year, month, day, extra
    match = _year_pat.search(v)
    year = match.group(0) if match else None
    return year, None, None, None


def parse_author(v):
    """Parse an author field"""
    chunks = v.split(',')
    name = chunks[0].strip()
    first = None
    suffix = None
    if len(chunks) > 1:
        first = chunks[1].strip()
    if len(chunks) == 3:
        suffix = chunks[2]
    return name, first, suffix


def remove_newlines(v):
    """Remove line breaks embedded in a text field

    Some sources, such as ACS, wrap long titles and abstracts over several
    lines. Each line break, together with the whitespace around it, is
    replaced by a single space, and leading and trailing whitespace is
    removed. Text without line breaks is returned unchanged, except for
    the stripping.

    Args:
        v (str) : the text to clean, for instance the output of get_title
            or get_abstract.
    """
    return _newline_pat.sub(' ', v).strip()


def _maybe_strip_newlines(value, strip_newlines):
    """Apply remove_newlines to value if strip_newlines is True"""
    return remove_newlines(value) if strip_newlines else value


def clean_reference(ref):
    """Remove trailing spaces and line breaks from the entries"""
    for k, v in ref.items():
        try:
            nv = v.strip()
        except AttributeError:
            nv = [el.strip() for el in v]
        ref[k] = nv
    return ref


def tag2string(ref, t):
    """Return the content of tag t as a string, 'NA' if the tag is not
    present"""

    if t in ref:
        if isinstance(ref[t], list):
            return " ".join(ref[t])
        else:
            return ref[t]
    else:
        return _missing_data

def tag2list(ref, t):
    """Return the content of tag t as a list, [] if the tag is not present
    """
    if t in ref:
        if isinstance(ref[t], list):
            return ref[t]
        else:
            return [ref[t]]
    else:
        return []

