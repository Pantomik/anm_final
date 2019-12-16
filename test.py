
from matplotlib.collections import LineCollection
from parsing import Parser
from plot import Plot
import matplotlib.pyplot as plt
import numpy as np

ROLLING = 40

KPI_WITH_CONNECTIONS = [
    '02e99bd4f6cfb33f', ## Total 95.94748059302127
    '1c35dbf57f55f5e4', ## Total 98.53709265597232
    '9ee5879409dccef9', ## Very low but Total 95.2329294565234
]

def check_with_connection(values, upperBand, lowerBand, STD):
    LIMIT_CHECK = 160

    res = []
    for i in range(0, len(values)):
        if values[i] > upperBand[i] or values[i] < lowerBand[i]:
            if values[i] > (upperBand[i] + STD[i]): res.append(3)
            else: res.append(1)
        else: res.append(0)
    for i in range(0, len(res)):
        if res[i] == 1 and i + 1 < len(res):
            if res[i - 1] == 0: res[i - 1] = 2
            if res[i + 1] == 0: res[i + 1] = 2
    for i in range(0, len(res)):
        if res[i] == 2: res[i] = 1
    saveI = -1
    for i in range(0, len(res)):
        if res[i] == 3:
            if saveI == -1:
                saveI = i
                continue
            if i - saveI <= LIMIT_CHECK:
                for j in range(saveI, i): res[j] = 3
            saveI = i
    for i in range(0, len(res)):
        if res[i] == 3: res[i] = 1
    return res

def check_without_connection(values, upperBand, lowerBand, STD):
    res = []
    for i in range(0, len(values)):
        if values[i] > upperBand[i] or values[i] < lowerBand[i]: res.append(1)
        else: res.append(0)
    for i in range(0, len(res)):
        if res[i] == 1 and i + 1 < len(res):
            if res[i - 1] == 0: res[i - 1] = 2
            if res[i + 1] == 0: res[i + 1] = 2
    for i in range(0, len(res)):
        if res[i] == 2: res[i] = 1
    return res

def compute_mean(values):
    cnt = 0
    for i in range(0, len(values)): cnt += values[i]
    return cnt / len(values)

def compute_std(values, mean):
    cnt = 0
    for i in range(0, len(values)): cnt += ((values[i] - mean) ** 2)
    return ((cnt / len(values)) ** 0.5)


def writeInFile(file, timestamp, kpi, predict):
    sep = ','
    
    dataLen = len(timestamp)

    for i in range(0, dataLen):
        rowText = str(kpi) + str(sep) + str(timestamp[i]) + str(sep) + str(predict[i]) + str('\n')
        file.write(rowText)

def main():
    p = Parser()
    data = p.build_test_set('datasets/test.csv')

    file = open('./results.csv',"w")
    firstRow = 'KPI ID,timestamp,predict\n'
    file.write(firstRow)
    for dataset in data:
        kpi = dataset.kpi
        timestamps = []
        values = []
        # label = []
        for elem in dataset:
            timestamps.append(elem.time)
            values.append(elem.value)
            # label.append(elem.label)
        upperBand = [-1 for a in range(0, len(values))]
        lowerBand = [-1 for a in range(0, len(values))]
        MA = [-1 for a in range(0, len(values))]
        STD = [-1 for a in range(0, len(values))]
        savedTimestamp = timestamps[0]
        nextTimestamp = savedTimestamp + 86400
        for i in range(0, len(values)):
            if upperBand[i] != -1: continue
            savedTimestamp = timestamps[i]
            nextTimestamp = savedTimestamp + 86400
            tmpValues = []
            tmpIndex = []
            tmpIndex.append(i)
            for j in range(i, len(values)):
                if nextTimestamp <= timestamps[j]:
                    savedTimestamp = nextTimestamp
                    nextTimestamp = nextTimestamp + 86400
                    tmpValues.append(values[j])
                    tmpIndex.append(j)
            mean = compute_mean(tmpValues)
            std = compute_std(tmpValues, mean)
            for index in tmpIndex:
                MA[index] = mean
                STD[index] = std
                upperBand[index] = mean + (2 * std)
                lowerBand[index] = mean - (2 * std)
        res = []

        if kpi in KPI_WITH_CONNECTIONS: res = check_with_connection(values, upperBand, lowerBand, STD)
        else: res = check_without_connection(values, upperBand, lowerBand, STD)

        writeInFile(file, timestamps, kpi, res)
        print(kpi,'Done')

        # compare = []
        # nbOfGoodFalse = 0
        # nbOfGoodTrue = 0
        # nbOfTrue = 0
        # nbOfFalse = 0
        # for i in range(0, len(label)):
        #     if label[i] == False:
        #         nbOfFalse += 1
        #         if label[i] == res[i]:
        #             compare.append('b')
        #             nbOfGoodFalse += 1
        #         else: compare.append('y')
        #     else:
        #         nbOfTrue += 1
        #         if label[i] == res[i]:
        #             compare.append('g')
        #             nbOfGoodTrue += 1
        #         else: compare.append('r')

        # print('Results for', kpi,':')
        # print('Not error found:', nbOfGoodFalse * 100 / nbOfFalse)
        # print('Error found:', nbOfGoodTrue * 100 / nbOfTrue)

        # t = np.arange(0, len(values))

        # lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(t[:-1], values[:-1], t[1:], values[1:])]
        # colored_lines = LineCollection(lines, colors=compare, linewidths=(2,))

        # fig, ax = plt.subplots(1, 1)
        # ax.add_collection(colored_lines)
        # ax.plot(t, upperBand, t, lowerBand)

        # fig.tight_layout()
        # plt.show()
        # break
 
if __name__ == '__main__':
    main()
