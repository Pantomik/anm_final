
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

import copy

TENMINUTES = 10 * 60

class Plot:
    KPI_IDS = ['02e99bd4f6cfb33f', '9bd90500bfd11edb',
    'da403e4e3f87c9e0', 'a5bf5d65261d859a', '18fbb1d5a5dc099d',
    '09513ae3e75778a3', 'c58bfcbacb2822d1', '1c35dbf57f55f5e4',
    '046ec29ddf80d62e', '07927a9a18fa19ae', '54e8a140f6237526',
    'b3b2e6d1a791d63a', '8a20c229e9860d0c', '769894baefea4e9e',
    '76f4550c43334374', 'e0770391decc44ce', '8c892e5525f3e491',
    '40e25005ff8992bd', 'cff6d3c01e6a6bfa', '71595dd7171f4540',
    '7c189dd36f048a6c', 'a40b1df87e3f1c87', '8bef9af9a922e0b3',
    'affb01ca2b4f0b45', '9ee5879409dccef9', '88cf3a776ba00e7c']

    def __init__(self, data, data_type):
        self._data = data
        self._data_type = data_type
    
    def __find_dataset(self, kpi_index):
        try:
            kpi_id = self.KPI_IDS[int(kpi_index)]
        except:
            kpi_id = '02e99bd4f6cfb33f'
        for dataset in self._data:
            if dataset.kpi != kpi_id: continue
            return dataset
        return None

    def __display_test(self, timestamps, values):
        _, ax = plt.subplots(1)
        ax.plot(timestamps, values)
        ax.autoscale_view()
        plt.xticks(np.arange(min(timestamps), max(timestamps), 1000000))
        plt.yticks(np.arange(min(values), max(values), 1))
        plt.show()

    def __display_train_and_result(self, timestamps, values, label):
        c = ['r' if a else 'b' for a in label]

        lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(timestamps[:-1], values[:-1], timestamps[1:], values[1:])]
        colored_lines = LineCollection(lines, colors=c, linewidths=(2,))

        _, ax = plt.subplots(1)
        ax.add_collection(colored_lines)
        ax.autoscale_view()
        plt.xticks(np.arange(min(timestamps), max(timestamps), 1000000))
        plt.yticks(np.arange(min(values), max(values), 10))
        plt.show()

    def __display_compare(self, timestamps, values, compare):
        lines = [((x0,y0), (x1,y1)) for x0, y0, x1, y1 in zip(timestamps[:-1], values[:-1], timestamps[1:], values[1:])]
        colored_lines = LineCollection(lines, colors=compare, linewidths=(2,))

        _, ax = plt.subplots(1)
        ax.add_collection(colored_lines)
        ax.autoscale_view()
        plt.xticks(np.arange(min(timestamps), max(timestamps), 1000000))
        plt.yticks(np.arange(min(values), max(values), 10))
        plt.show()

    def __get_data(self, dataset):
        timestamps = []
        values = []
        label = []
        for elem in dataset:
            timestamps.append(elem.time)
            values.append(elem.value)
            if self._data_type == 'train' or self._data_type == 'compare': label.append(elem.label)
        return timestamps, values, label

    def compare_results(self, kpi_index, res):
        dataset = self.__find_dataset(kpi_index)
        if dataset == None:
            print("An error occured. No dataset found.")
            return
        timestamps, values, label = self.__get_data(dataset)
        if len(label) != len(res):
            print("Label and result doesn't have the same size.")
            return
        compare = []
        for i in range(0, len(label)):
            if label[i] == res[i] and label[i] == True: compare.append('g')
            elif label[i] == res[i] and label[i] == False: compare.append('b')
            else: compare.append('r')
        self.__display_compare(timestamps, values, compare)

    def display_plot(self, kpi_index):
        dataset = self.__find_dataset(kpi_index)
        if dataset == None:
            print("An error occured. No dataset found.")
            return
        timestamps, values, label = self.__get_data(dataset)
        if self._data_type == 'test': self.__display_test(timestamps, values)
        else: self.__display_train_and_result(timestamps, values, label)