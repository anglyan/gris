from .gris import ris_boundtags


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
