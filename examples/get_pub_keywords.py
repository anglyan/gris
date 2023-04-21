from gris import get_keywords, read_ris
import sys

ref_list = read_ris(sys.argv[1])
for ref in ref_list:
    py = get_keywords(ref)
    print(py)
    