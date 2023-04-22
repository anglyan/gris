#Copyright (c) 2013 Angel Yanguas-Gil
#This program is free software, licensed under GPLv2 or later.
#A copy of the GPLv2 license is provided in the root directory of
#the source code.

"""Parse WOK and Refman's RIS files"""

import re
import csv

woktag = "^[A-Z][A-Z0-9] |^ER$|^EF$"
ristag = "^[A-Z][A-Z0-9]  -"

wokpat = re.compile(woktag)
rispat = re.compile(ristag)

ris_boundtags = ('TY', 'ER')
wok_boundtags = ('PT', 'ER')

wok_ignoretags = ['FN', 'VR', 'EF']
ris_ignoretags = []

missing_string = 'NA'

def read_ris(filename, wok=False):
    """Parse a ris file and return a list of entries.

    Entries are codified as dictionaries whose keys are the
    different tags. For single line and singly ocurring tags,
    the content is codified as a string. In the case of multiline
    or multiple key ocurrences, the content is returned as a list
    of strings.

    Args:
        filename (str) : input ris file
        wok (:obj:`bool`, optional) : old WebofKnowledge's other document
            format is used if True. Defaults False.

    """

    if wok:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[2:].strip()
        istag = lambda line: (wokpat.match(line) != None )
        starttag, endtag = wok_boundtags
        ignoretags = wok_ignoretags
    else:
        gettag = lambda line: line[0:2]
        getcontent = lambda line: line[6:].strip()
        istag = lambda line: (rispat.match(line) != None )
        starttag, endtag = ris_boundtags
        ignoretags = ris_ignoretags

    filelines = open(filename, encoding='utf-8-sig', mode='r').readlines()
    #WOK saves text files as utf8 with BOM, BOM is not handled automatically
    #by python 3, so we have to use utf-8-sig to deal with it.

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
                    #Dealing with multiline records
                    if isinstance(current[tag], list):
                        current[tag][-1] += "\n" + line.strip()
                    else:
                        current[tag] += "\n" + line.strip()
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
                if tag in current:
                    if not isinstance(current[tag], list):
                        current[tag] = [current[tag]]
                    current[tag].append(getcontent(line))
                else:
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


def get_keywords(ref):
    """Return a list of keywords"""
    if 'KW' in ref:
        return tag2list(ref, 'KW')
    else:
        return []


def get_abstract(ref):
    """Return the abstract"""
    return tag2string(ref, 'AB')


def get_pubyear(ref):
    """Return the publication year"""
    py = tag2string(ref, 'PY')
    if py == missing_string:
        py = tag2string(ref, 'C6')
        if py != missing_string:
            py = py.split()[1]
    return py

def get_journal(ref):
    """Return the publication year"""
    py = tag2string(ref, 'JO')
    if py == missing_string:
        py = tag2string(ref, 'T2')
    return py

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


def get_country(add):
    """Extract the country from a ris address field
    """

    rpc = add.split(',')[-1][:-1].strip().upper()
    if ' USA' in rpc:
        rpc = 'USA'
    elif len(rpc.split()[0]) == 2:
        rpc = 'USA'
    return rpc


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
