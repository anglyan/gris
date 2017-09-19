#Copyright (c) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

"""Parse WOK and Refman's RIS files"""

import re
import csv

woktag = "^[A-Z][A-Z0-9] |^ER$|^EF$"
ristag = "^[A-Z][A-Z0-9]  - "

wokpat = re.compile(woktag)
rispat = re.compile(ristag)

ris_boundtags = ('TY', 'ER')
wok_boundtags = ('PT', 'ER')

wok_ignoretags = ['FN', 'VR', 'EF']
ris_ignoretags = []

ristags = {'TY': "Record kind",
        'A2': "Secondary Author",
        'A3': "Tertiary Author",
        'A4': "Subsidiary Author",
        'AB': "Abstract",
        'AD': "Author Address",
        'AN': "Accession Number",
        'AU': "Author",
        'C1': "Custom 1",
        'CA': "Caption",
        'CN': "Call Number",
        'CY': "Place Published",
        'DA': "Date",
        'DB': "Name of Database",
        'DO': "DOI",
        'DP': "Database Provider",
        'ET': "Edition",
        'J2': "Alternate Title",
        'KW': "Keywords",
        'L1': "File Attachments",
        'L4': "Figure",
        'LA': "Language",
        'LB': "Label",
        'IS': "Number",
        'M3': "Type of Work",
        'N1': "Notes",
        'NV': "Number of Volumes",
        'OP': "Original Publication",
        'PB': "Publisher",
        'PY': "Year",
        'RI': "Reviewed Item",
        'RN': "Research Notes",
        'RP': "Reprint Edition",
        'SE': "Version",
        'SN': "ISBN",
        'SP': "Pages",
        'ST': "Short Title",
        'T2': "Dictionary Title",
        'TA': "Translated Author",
        'TI': "Title",
        'TT': "Translated Title",
        'UR': "URL",
        'VL': "Volume",
        'Y2': "Access Date",
        'ER': "[End of Reference]"
        }

missing_string = 'NA'

def read_ris(filename, wok=True):
    """Parse a ris file and return a list of entries.
    
    Entries are codified as dictionaries whose keys are the
    different tags. For single line and singly ocurring tags,
    the content is codified as a string. In the case of multiline
    or multiple key ocurrences, the content is returned as a list
    of strings.

    Keyword arguments:
    filename -- input ris file
    wok -- flag, Web of Knowledge format is used if True, otherwise
           Refman's RIS specifications are used.
    
    """

    if wok:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[2:]
        istag = lambda line: (wokpat.match(line) != None )
        starttag, endtag = wok_boundtags
        ignoretags = wok_ignoretags
    else:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[6:]
        istag = lambda line: (rispat.match(line) != None )
        starttag, endtag = ris_boundtags
        ignoretags = ris_ignoretags

    filelines = open(filename, 'r').readlines()
    #Corrects for BOM in utf-8 encodings while keeping an 8-bit
    #string representation
    st = filelines[0]
    if (st[0], st[1], st[2]) == ('\xef', '\xbb', '\xbf'):
        filelines[0] = st[3:]

    inref = False
    tag = None
    refs = []
    current = {}
    ln = 0

    for line in filelines:
        ln += 1
        if not istag(line):
            #It is not a tag
            if len(line.strip()) == 0:
                #Empty line
                continue
            if inref:
                #Active reference
                if tag == None:
                    text = "Expected tag in line %d:\n %s" %(ln, line)
                    raise IOError(text)
                else:
                    #Active tag
                    if hasattr(current[tag], '__iter__'):
                        current[tag].append(line.strip())
                    else:
                        current[tag] = [current[tag], line.strip()]
            else:
                text = "Expected start tag in line %d:\n %s" %(ln, line)
                raise IOError(text)
        else:
            #Get the new tag
            tag = gettag(line)
            if tag in ignoretags:
                continue
            elif tag == endtag:
                #Close the active entry and append it to the entry list
                refs.append(current)
                current = {}
                inref = False
            elif tag == starttag:
                #New entry
                if inref:
                    text = "Missing end of record tag in line %d:\n %s" % (
                            ln, line)
                    raise IOError(text)
                current[tag] = getcontent(line)
                inref = True
            else:
                if not inref:
                    text = "Invalid start tag in line %d:\n %s" %(ln, line)
                    raise IOError(text)
                current[tag] = getcontent(line)

    refs = [clean_reference(r) for r in refs]

    return refs

def clean_reference(ref):
    """Remove trailing spaces and line breaks from the entries"""
    for k,v in ref.items():
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
        return missing_string

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

def get_authors(ref):
    """Return a list of the authors"""
    if 'AF' in ref:
        return tag2list(ref, 'AF')
    else:
        return tag2list(ref, 'AU')

def get_abstract(ref):
    """Return the abstract"""
    return tag2string(ref, 'AB')

def get_pubyear(ref):
    """Return the publication year"""
    return tag2string(ref, 'PY')

def get_title(ref):
    """Return the pubication title"""
    return tag2string(ref, 'TI')

def get_volume(ref):
    """Return the publication volume"""
    return tag2string(ref, 'VL')

def get_issue(ref):
    """Return the publication issue"""
    return tag2string(ref, 'IS')

def get_page(ref):
    """Return the page and, if not present, the article number"""
    if 'BP' in ref:
        return tag2string(ref, 'BP')
    else:
        return tag2string(ref, 'AR')

def write_key(key, value):
    """Return a string with the key, value in the WOK RIS format
    """

    if isinstance(value, list):
        lines = [key + " " + value[0].strip()]
        for val in value[1:]:
            lines.append("   " + val.strip())
        return lines
    else:
        return [key + " " + value.strip()]

def write_ref(entry):
    """Return a string with the content of the reference
    in WOK RIS format.

    entry is a dictionary where tags are keys and the values are
    either lists or strings containing the corresponding bibliographic
    data
    """

    entrylines = write_key('PT', entry['PT'])
    for k, v in entry.items():
        if k != 'PT':
            entrylines.extend(write_key(k, v))
    entrylines.append('ER')
    return entrylines

def write_ris(entrylist):
    """Write a list of entries in the wok ris file format
    
    write_ris uses as an input a list of entries as codified
    using read_ris, returning a list of strings. The current version
    returns a wok-compatible ris format.

    """
    header = ['FN Thompsom Reuters Web of Knowledge',
             'VR 1.0']
    filelines = header
    for entry in entrylist:
        filelines.extend(write_ref(entry))
        filelines.append("")
    filelines.append('EF')
    return filelines


def get_country(add):
    """Extract the country from a ris address field
    """

    rpc = add.split(',')[-1][:-1].strip().upper()
    if ' USA' in rpc:
        rpc = 'USA'
    elif len(rpc.split()[0]) == 2:
        rpc = 'USA'
    return rpc

def recordtolist(i, ref):
    """Transform a single record into a 2D list"""

    title = tag2string(ref, 'TI')
    authors = [au.upper() for au in tag2list(ref, 'AU')]
    categories = [c.strip() for c in tag2string(ref, 'WC').split(';')]
    source = tag2string(ref, 'SO')
    dt = tag2string(ref, 'DT')
    tc = tag2string(ref, 'TC')
    pubyear = tag2string(ref, 'PY')
    aff = tag2list(ref, 'C1')
    reprint = tag2string(ref, 'RP')
    rpc = get_country(reprint)
    affc = [get_country(ai) for ai in aff]
    doi = tag2string(ref, 'DI')
    if len(aff) == 0:
        aff = ['NA']
        affc = ['NA']
    if len(categories) == 0:
        categories = ['NA']
    names = [an.split(',')[0].strip() if ',' in an else an for an in authors]
    lines = [[str(i), dt, source,
            pubyear, title, doi, tc, reprint, rpc, au, name, 
            aff[0], affc[0], categories[0]]
            for (au, name) in zip(authors, names)]
    lines2 = [[str(i), dt, source, pubyear,
            title, doi, tc, reprint, rpc, authors[0],
            names[0], ai, aci, categories[0]] for ai,aci in zip(aff[1:], affc[1:])]
    lines3 = [[str(i), dt, source, pubyear,
            title, doi, tc, reprint, rpc, authors[0],
            names[0], aff[0], affc[0], c] for c in categories[1:]]

    return lines + lines2 + lines3


def refs2csv(refs, filename):
    """Save a list of references to a csv file
    """

    table = [["Ref #", "Document type", "Source", "Year", "Title",
            "DOI", "Times cited", "Reprint Author", "Reprint country", 
            "Author, complete",
            "Author name", "Affiliation", "Affiliation country",
            "Category"]]
    for i, ref in enumerate(refs):
        r = ristocsv(i, ref)
        table.extend(r)
    out = csv.writer(open(csvname, 'w'))
    out.writerows(table)
    return table



if __name__ == '__main__':

    import sys

    if len(sys.argv) > 2:
        if sys.argv[2] == 'ris':
            wok=False
        else:
            wok=True
    else:
        wok=True
    refs = read_ris(sys.argv[1], wok)
    print(len(refs))
    authors = [r['AU'] for r in refs]
    for a in authors:
        print(a)



