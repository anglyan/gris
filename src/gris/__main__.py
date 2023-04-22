from .gris import read_ris

import sys

rlist = read_ris(sys.argv[1], False)

if len(sys.argv) !=3:
    print("""Usage: python -m gris key""")
else:
    tag = sys.argv[2]
    for i, ref in enumerate(rlist):
        value = ref.get(tag, 'NA')
        if not isinstance(value, list):
            value = [value]
        for val in value:
            line = str(i+1)+ "," + '"{}"'.format(val)
            print(line)



