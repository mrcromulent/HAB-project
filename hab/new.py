from config import Columns, formatter_funcs, fp
from datetime import datetime
from collections import OrderedDict
import pprint


callsign = "YERRA"


def read_line(ln):
    d = OrderedDict()
    ln_list = ln.split(',')

    for k, item in Columns.__members__.items():
        func = formatter_funcs[item]
        d[item] = func(ln_list[item.value])

    return d


pp = pprint.PrettyPrinter(indent=4)
memory = []


with open(fp, "r") as f:
    for i, line in enumerate(f):
        if i < 21_000:
            if line.startswith("$$"):
                if line.find(callsign) != -1:
                    data = read_line(line)

                    if len(memory) < 10:
                        memory.append(data)
                    else:

                        packet_no = data[Columns.PACKET]

                        if packet_no > memory[-1][Columns.PACKET]:
                            memory.pop(0)
                            memory.append(data)

            else:
                print(f"Ignored: {line}")

print(pp.pformat(memory))

if __name__ == "__main__":
    pass
