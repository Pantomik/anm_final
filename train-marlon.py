
from matplotlib.collections import LineCollection
from parsing import Parser
from plot import Plot
import matplotlib.pyplot as plt
import numpy as np

KPI_WITH_PERSONNAL_BANDS = [
    '02e99bd4f6cfb33f', ## Total 95.94748059302127
    '9bd90500bfd11edb',
]

KPI_WITH_BOLLINGER_BANDS = [
]

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

def personal_bands(values, timestamps):
    print('in')
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
            upperBand[index] = mean + (3 * std)
            lowerBand[index] = mean - (1.75 * std)
    return MA, STD, upperBand, lowerBand

def bollinger_bands(values):
    ROLLING = 200

    upperBand = []
    lowerBand = []
    MA = []
    STD = []
    for i in range(0, len(values)):
        start = i - ROLLING
        end = i
        if start < 0:
            start = 0
            end = i + 1
        mean = compute_mean(values[start:end])
        std = compute_std(values[start:end], mean)
        MA.append(mean)
        STD.append(std)
        upperBand.append(mean + (2 * std))
        lowerBand.append(mean - (2 * std))
    return MA, STD, upperBand, lowerBand

def main():
    p = Parser()
    data = p.build_train_set('datasets/train.csv')
    cnt = 0

    for dataset in data:
        cnt += 1
        if cnt != 2: continue
        kpi = dataset.kpi
        timestamps = []
        values = []
        label = []
        for elem in dataset:
            timestamps.append(elem.time)
            values.append(elem.value)
            label.append(elem.label)

        if kpi in KPI_WITH_PERSONNAL_BANDS:
            MA, STD, upperBand, lowerBand = personal_bands(values, timestamps)
        elif kpi in KPI_WITH_BOLLINGER_BANDS:
            MA, STD, upperBand, lowerBand = bollinger_bands(values)


        resWithConnections = check_with_connection(values, upperBand, lowerBand, STD)
        resWithoutConnections = check_without_connection(values, upperBand, lowerBand, STD)


        compare = []
        nbOfGoodTrueWithConnection = 0
        nbOfGoodFalseWithConnection = 0
        nbOfGoodTrueWithoutConnection = 0
        nbOfGoodFalseWithoutConnection = 0
        nbOfTrue = 0
        nbOfFalse = 0
        for i in range(0, len(label)):
            if label[i] == False:
                nbOfFalse += 1
                if resWithConnections[i] == False:
                    compare.append('b')
                    nbOfGoodFalseWithConnection += 1
                if resWithoutConnections[i] == False:
                    compare.append('b')
                    nbOfGoodFalseWithoutConnection += 1
                else: compare.append('y')
            else:
                nbOfTrue += 1
                if resWithConnections[i] == True:
                    compare.append('g')
                    nbOfGoodTrueWithConnection += 1
                if resWithoutConnections[i] == True:
                    compare.append('g')
                    nbOfGoodTrueWithoutConnection += 1
                else: compare.append('r')

        print('\n\nResults for', kpi,'with connection :')
        print('Not error found:', nbOfGoodFalseWithConnection * 100 / nbOfFalse)
        print('Error found:', nbOfGoodTrueWithConnection * 100 / nbOfTrue)
        print('Total:', (nbOfGoodFalseWithConnection + nbOfGoodTrueWithConnection) * 100 / (nbOfFalse + nbOfTrue))
        print('\nResults for', kpi,'without connection :')
        print('Not error found:', nbOfGoodFalseWithoutConnection * 100 / nbOfFalse)
        print('Error found:', nbOfGoodTrueWithoutConnection * 100 / nbOfTrue)
        print('Total:', (nbOfGoodFalseWithoutConnection + nbOfGoodTrueWithoutConnection) * 100 / (nbOfFalse + nbOfTrue))

        t = np.arange(0, len(values))

        lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(t[:-1], values[:-1], t[1:], values[1:])]
        colored_lines = LineCollection(lines, colors=compare, linewidths=(2,))

        c = ['r' if a else 'b' for a in label]

        linesTmp = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(t[:-1], values[:-1], t[1:], values[1:])]
        colored_linesTmp = LineCollection(linesTmp, colors=c, linewidths=(2,))

        fig, ax = plt.subplots(1, 1)
        # ax.add_collection(colored_lines)
        ax.add_collection(colored_linesTmp)
        ax.plot(t, MA, t, upperBand, t, lowerBand)
        # ax.plot(t, upperBand, t, lowerBand)

        fig.tight_layout()
        plt.show()
        break
 
if __name__ == '__main__':
    main()
