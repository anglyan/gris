from gris import get_title, read_ris
import sys

ref_list = read_ris(sys.argv[1])
for ref in ref_list:
    py = get_title(ref)
    print(py)
    