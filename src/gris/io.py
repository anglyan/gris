from .gris import ris_boundtags, tag2list, tag2string
import json

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

