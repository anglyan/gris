from gris import get_abstract, read_ris
import sys

ref_list = read_ris(sys.argv[1])
for ref in ref_list:
    py = get_abstract(ref)
    print(py)
    