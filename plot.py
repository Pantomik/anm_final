import csv
import sys
from datetime import datetime
import os

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

TENMINUTES = 10 * 60

def parseFiles(fileName, data):
    print("Parsing ...")
    cnt = -1
    with open(fileName) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        kpi = ''
        for row in readCSV:
            cnt += 1
            if cnt == 0:
                for col in row:
                    data.append([col, list()])
                continue
            if cnt == 1: kpi = row[3]
            if row[3] != kpi: break
            for i in range(0, len(row)):
                if data[i][0] == "timestamp": data[i][1].append(int(row[i]))
                if data[i][0] == "value": data[i][1].append(float(row[i]))
                if data[i][0] == "label": data[i][1].append(bool(int(row[i])))
                if data[i][0] == "KPI ID": data[i][1].append(str(row[i]))
    print(cnt)
    print("Done!\n")
    return data, cnt

if __name__ == "__main__":
    fileName = "./datasets/train.csv"

    data = list()
    data, size = parseFiles(fileName, data)

    for col in data:
        if col[0] == "timestamp":
            timestamps = col[1]
        if col[0] == "value":
            value = col[1]
        if col[0] == "KPI ID":
            kpi = col[1]
        if col[0] == "label":
            label = col[1]

    n = size
    x = timestamps
    y = value
    annotation = label

    c = ['r' if a else 'g' for a in annotation]

    lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(x[:-1], y[:-1], x[1:], y[1:])]
    colored_lines = LineCollection(lines, colors=c, linewidths=(2,))

    fig, ax = plt.subplots(1)
    ax.add_collection(colored_lines)
    ax.autoscale_view()
    plt.xticks(np.arange(min(timestamps), max(timestamps), 1000000))
    plt.yticks(np.arange(min(value), max(value), 1))
    plt.show()

    print('Done!\n')