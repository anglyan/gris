from gris import read_ris, write_ris
from gris.io import write_ref
import sys

ref_list = read_ris(sys.argv[1])
out = write_ref(ref_list[0])
print(out)
out_name = sys.argv[2]
write_ris(out_name, ref_list)
ref_list = read_ris(out_name)
