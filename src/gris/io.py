import json
import re
import csv
from .ris import clean_reference

woktag = "^[A-Z][A-Z0-9] |^ER$|^EF$"
ristag = "^[A-Z][A-Z0-9]  -"

wokpat = re.compile(woktag)
rispat = re.compile(ristag)

ris_boundtags = ('TY', 'ER')
wok_boundtags = ('PT', 'ER')

wok_ignoretags = ['FN', 'VR', 'EF']
ris_ignoretags = []

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



def write_key(key):
    return "{}  -".format(key)


def write_entry(key, value):
    """Return a string with the key, value
    """

    if not isinstance(value, list):
        value = [value]
    
    lines = []
    key_str = write_key(key)
    lines = [key_str + " " + val.strip() for val in value]
    return lines


def write_ref(entry):
    """Return a string with the content of the reference
    in RIS format.

    entry is a dictionary where tags are keys and the values are
    either lists or strings containing the corresponding bibliographic
    data
    """

#    entrylines = write_key('PT', entry['PT'])
    starttag, endtag = ris_boundtags

    entrylines = write_entry(starttag, entry[starttag])
    for k, v in entry.items():
        if k != starttag:
            entrylines.extend(write_entry(k, v))
    entrylines.append(write_key(endtag))
    return entrylines


def write_json(file_name, refs):
    with open(file_name, 'w') as f:
        json.dump(refs, f, indent=4)
        f.close()


def load_json(file_name):
    with open(file_name, 'r') as f:
        refs = json.load(f)
        f.close()
        if not isinstance(refs, list):
            refs = [refs]
        return refs
    

def write_ris(file_name, entrylist):
    """Write a list of entries in the RIS file format

    write_ris uses as an input a list of entries as codified
    using read_ris, returning a list of strings.

    """
    with open(file_name, 'w') as f:
        filelines = []
        for entry in entrylist:
            filelines.extend(write_ref(entry))
            filelines.append("")
        f.write("\n".join(filelines))
        f.close()
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


# def recordtolist(i, ref):
#     """Transform a single record into a 2D list"""

#     title = tag2string(ref, 'TI')
#     authors = [au.upper() for au in tag2list(ref, 'AU')]
#     categories = [c.strip() for c in tag2string(ref, 'WC').split(';')]
#     source = tag2string(ref, 'SO')
#     dt = tag2string(ref, 'DT')
#     tc = tag2string(ref, 'TC')
#     pubyear = tag2string(ref, 'PY')
#     aff = tag2list(ref, 'C1')
#     reprint = tag2string(ref, 'RP')
#     rpc = get_country(reprint)
#     affc = [get_country(ai) for ai in aff]
#     doi = tag2string(ref, 'DI')
#     if len(aff) == 0:
#         aff = ['NA']
#         affc = ['NA']
#     if len(categories) == 0:
#         categories = ['NA']
#     names = [an.split(',')[0].strip() if ',' in an else an for an in authors]
#     lines = [[str(i), dt, source,
#             pubyear, title, doi, tc, reprint, rpc, au, name,
#             aff[0], affc[0], categories[0]]
#             for (au, name) in zip(authors, names)]
#     lines2 = [[str(i), dt, source, pubyear,
#             title, doi, tc, reprint, rpc, authors[0],
#             names[0], ai, aci, categories[0]] for ai,aci in zip(aff[1:], affc[1:])]
#     lines3 = [[str(i), dt, source, pubyear,
#             title, doi, tc, reprint, rpc, authors[0],
#             names[0], aff[0], affc[0], c] for c in categories[1:]]

#     return lines + lines2 + lines3


# def refs2csv(refs, filename):
#     """Save a list of references to a csv file
#     """

#     table = [["Ref #", "Document type", "Source", "Year", "Title",
#             "DOI", "Times cited", "Reprint Author", "Reprint country",
#             "Author, complete",
#             "Author name", "Affiliation", "Affiliation country",
#             "Category"]]
#     for i, ref in enumerate(refs):
#         r = ristocsv(i, ref)
#         table.extend(r)
#     out = csv.writer(open(csvname, 'w'))
#     out.writerows(table)
#     return table

