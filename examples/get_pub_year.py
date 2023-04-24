from gris import get_pubyear, read_ris, parse_year
import sys

ref_list = read_ris(sys.argv[1])
for ref in ref_list:
    py = get_pubyear(ref)
    y, m, d, ex = parse_year(py)
    print(py, y, m, d, ex)

