from gris import read_ris
from gris.io import write_json, load_json, write_ris
import sys

ref_list = read_ris(sys.argv[1])
out_name = sys.argv[2]
write_json(out_name, ref_list)
refs = load_json(out_name)
write_ris(out_name + ".ris", refs)
