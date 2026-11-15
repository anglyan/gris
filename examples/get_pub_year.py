from gris import get_pubdate, get_pubyear, read_ris, parse_pubyear
import sys

ref_list = read_ris(sys.argv[1])
for ref in ref_list:
    pd = get_pubdate(ref)
    y, m, d, ex = parse_pubyear(pd)
    print(pd, get_pubyear(ref), m, d, ex)

