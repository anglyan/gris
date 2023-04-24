from gris import get_authors, read_ris, parse_year, parse_author
import sys

ref_list = read_ris(sys.argv[1])
for i, ref in enumerate(ref_list, start=1):
    au_list = get_authors(ref)
    for au in au_list:
        n, f, pre = parse_author(au)
        print(i, au, " : ", n, f, pre)

