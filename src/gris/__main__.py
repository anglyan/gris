from .gris import read_ris

import sys

rlist = read_ris(sys.argv[1], False)
if len(sys.argv) > 2:
    tags = sys.argv[2:]
    for ref in rlist:
        print(",".join([str(ref.get(tag,'NA')) for tag in tags]))



