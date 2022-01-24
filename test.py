import itertools
import pandas as pd
from statistics import median

l = [{'uuid': 'D20220106-S00026-C2000', 'id': '00026', 'capacity': '2000', 'esr': '0.2', 'voltage': '4.5', 'device': 'MCC'}, {'uuid': 'D20220106-S00013-C2000', 'id': '00013', 'capacity': '2000', 'esr': '0.2', 'voltage': '4.5', 'device': 'MCC'}, {'uuid': 'D20211125-S00012-C2640', 'id': '00012', 'capacity': '2640', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00010-C2940', 'id': '00010', 'capacity': '2940', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00009-C2340', 'id': '00009', 'capacity': '2340', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00008-C2850', 'id': '00008', 'capacity': '2850', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00007-C2550', 'id': '00007', 'capacity': '2550', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00006-C2750', 'id': '00006', 'capacity': '2750', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00005-C2950', 'id': '00005', 'capacity': '2950', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S000003-C3100', 'id': '000003', 'capacity': '3100', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S00004-C2900', 'id': '00004', 'capacity': '2900', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S000001-C3000', 'id': '000001', 'capacity': '3000', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}, {'uuid': 'D20211125-S000002-C3100', 'id': '000002', 'capacity': '3100', 'esr': '0.1', 'voltage': '4.2', 'device': 'Liitokala'}]

print(len(l))

series = 4
paralel = 3


def calculate_pack(cells, s, p):
    count = s * p
    available = sorted(cells, key=lambda b: int(b['capacity']), reverse=True)[:count]

    paralel_series = []
    for i in range(s):
        paralel_series.append([])
        for j in range(p):
            paralel_series[i].append(available[i + s * j])

    pack = dict()
    cell = 1
    for par in paralel_series:
        print()
        print("Cell Numer: %s" % cell)
        pack[cell] = []
        for unit in par:
            pack[cell].append(unit)
            # print(unit)

        cell += 1

    return pack


calculate_pack(l, series, paralel)
