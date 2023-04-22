from .gris import read_ris, tag2string

import sys
import tokenize
from io import BytesIO

rlist = read_ris(sys.argv[1], False)
if len(sys.argv) > 2:
    tags = sys.argv[2:]
    for ref in rlist:
        print(",".join([tag2string(ref, tag) for tag in tags]))



