#Copyright (c) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

"""Methods to operate with the Refman RIS data format"""

import re

_missing_data = 'NA'
_year_pat = re.compile(r'(?<!\d)\d{4}(?!\d)')

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


def get_title(ref):
    """Return the pubication title"""
    return tag2string(ref, 'TI')


def get_authors(ref):
    """Return a list of the authors"""
    if 'AU' in ref:
        return tag2list(ref, 'AU')
    else:
        return tag2list(ref, 'A1')


def get_journal(ref):
    """Return the journal"""
    py = tag2string(ref, 'JO')
    if py == _missing_data:
        py = tag2string(ref, 'T2')
    if py == _missing_data:
        py = tag2string(ref, 'JF')
    elif py == _missing_data:
        py = tag2string(ref, 'JA')
    return py


def get_volume(ref):
    """Return the publication volume"""
    return tag2string(ref, 'VL')


def get_issue(ref):
    """Return the publication issue"""
    return tag2string(ref, 'IS')


def get_pubdate(ref):
    """Return the raw publication date string, 'NA' if not present.

    Tags are tried in order of preference: PY, Y1 and DA. Zotero exports
    the year in PY and the full date in DA, and may leave PY out when
    it cannot parse the date, so DA is used as a last resort.
    """
    for tag in ('PY', 'Y1', 'DA'):
        value = tag2string(ref, tag).strip()
        if value and value != _missing_data and _year_pat.search(value):
            return value
    return _missing_data


def get_pubyear(ref):
    """Return the four digit publication year as a string, 'NA' if it
    cannot be determined"""
    match = _year_pat.search(get_pubdate(ref))
    return match.group(0) if match else _missing_data


def get_startpage(ref):
    """Return the start page and, if not present, the article number"""
    return tag2string(ref, 'SP')


def get_endpage(ref):
    """Return the end pager"""
    return tag2string(ref, 'EP')


def get_abstract(ref):
    """Return the abstract"""
    if 'AB' in ref:
        return tag2string(ref, 'AB')
    else:
        return tag2string(ref, 'N2')


def get_keywords(ref):
    """Return a list of keywords"""
    if 'KW' in ref:
        return tag2list(ref, 'KW')
    else:
        return []


def parse_pubyear(v):
    """Parse a publication year field"""
    chunks = v.split('/')
    year = chunks[0].strip()
    month = None
    day = None
    extra = None
    if len(chunks) > 1:
        month = chunks[1].strip()
    if len(chunks) > 2:
        day = chunks[2].strip()
    if len(chunks) == 4:
        extra = chunks[3].strip()
    return year, month, day, extra


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

