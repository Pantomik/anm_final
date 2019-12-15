
from scipy.interpolate import interp1d
from datetime import datetime, timedelta
from random import uniform

import numpy as np


MODEL_PATH = 'models.json'


ONE_WEEK_DELTA = timedelta(days=7)

# EVAL_RAW, EVAL_DISTANCE, EVAL_PERIOD, EVAL_SPREAD, SIZE_EVAL = range(5)
EVAL_RAW, EVAL_DISTANCE, EVAL_SPREAD, SIZE_EVAL = range(4)


def get_one_week_forward(time):
    return (datetime.fromtimestamp(time) + ONE_WEEK_DELTA).timestamp()


class DataObj:
    POTENTIAL_SPREADING = 10

    __slots__ = ('_parent', '_idx', '_time', '_value', '_label', '_potential')

    def __init__(self, parent, idx: int, timestamp, value, label=None):
        assert isinstance(parent, DataObjSet)
        self._parent = parent
        self._idx = idx
        self._time = int(timestamp)
        self._value = float(value)
        self._potential = [0.0 for _ in range(SIZE_EVAL)]
        self._label = label
        if label is not None:
            self._label = int(label) == 1

    def __repr__(self):
        label = ''
        if self._label is not None:
            label = ' ' + str(self._label)
        return f'<{self.kpi}> {self.time}: {self.value} {label}'

    @property
    def potential(self):
        coefficients = self._parent.coefficients
        ret = sum(self._potential[i] * coefficients[i] for i in range(SIZE_EVAL))
        ret = ret / sum(coefficients)
        return ret

    @property
    def time(self):
        return self._time

    @property
    def value(self):
        return self._value

    @property
    def kpi(self):
        return self._parent.kpi

    @property
    def label(self):
        return self._label

    def export_string(self):
        potential = 1 if self.potential > 0.0 else 0
        return '{0},{1},{2}\n'.format(self.kpi, self.time, potential)

    def potential_flag(self, key: int, potential: float, recursive=False):
        self._potential[key] += potential
        if recursive:
            for pad in range(1, self.POTENTIAL_SPREADING):
                pad += 2
                new = potential / (pad * 0.35)
                self._parent[self._idx - int(pad)].potential_flag(EVAL_SPREAD, new, False)
                self._parent[self._idx + int(pad)].potential_flag(EVAL_SPREAD, new, False)


class DataObjContainer:
    def __init__(self, kpi, coefficients):
        assert isinstance(coefficients, list)
        self._keys = None
        self._elements = {}
        self._kpi = kpi
        while len(coefficients) < SIZE_EVAL:
            coefficients.append(1.0)
        self._coefficients = coefficients

    def __iter__(self):
        return iter(self._elements.values())

    def __len__(self):
        return len(self._elements)

    def __repr__(self):
        return f'<{type(self).__name__}> ({len(self._elements)})'

    def __getitem__(self, item):
        if self._keys is None:
            self._keys = sorted(self._elements.keys())
        return self._elements[self._keys[item]]

    @property
    def coefficients(self):
        return self._coefficients.copy()

    @property
    def kpi(self):
        return self._kpi

    def add(self, element):
        if not isinstance(element, DataObj):
            raise TypeError('Element should be a DataObj')
        if element.time in self._elements.keys():
            raise RuntimeError('Two elements with the same timestamp')
        self._keys = None
        self._elements[element.time] = element


class DataObjSet(DataObjContainer):
    IGNORE_START = 50
    MAXIMUM_THRESHOLD = 1
    RAW_LEVELS = ((0.0, -0.1), (0.6, 0.17), (0.7, 0.02), (0.8, 0.03), (0.9, 0.035), (1.0, 0.04))
    SMOOTHING_MAX_RANGE = 100
    DISTANCE_INTERVAL_PERCENT = 0.21

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __start(self):
        head_x, head_y = [], []
        tail_x, tail_y = [], []
        for idx in range(self.IGNORE_START):
            head_e, tail_e = self[idx], self[self.IGNORE_START + idx]
            head_x.append(head_e.time)
            head_y.append(head_e.value)
            tail_x.append(tail_e.time)
            tail_y.append(tail_e.value)
        return (head_x, head_y), (tail_x, tail_y)

    def __apply_potential_modification(self, percent):
        total_value = 0.0
        for level, value in self.RAW_LEVELS:
            if percent < level:
                break
            total_value += value
        return total_value

    def __compare(self, key, evaluated: DataObj, reference):
        x, y = reference
        cubic = interp1d(x, y)
        expected = cubic(evaluated.time)
        diff = abs(evaluated.value - expected)
        if evaluated.value != 0:
            diff = diff / evaluated.value
        potential = self.__apply_potential_modification(diff)
        evaluated.potential_flag(key, potential)

    def __raw_evaluation(self):
        i = self.IGNORE_START
        (head_x, head_y), (tail_x, tail_y) = self.__start()
        next_value = self.IGNORE_START * 2
        size = len(self._elements) - next_value
        while i < size:
            tail_x.pop(0), tail_y.pop(0)
            evaluated, next_element = self[i], self[next_value + i]
            tail_x.append(next_element.time)
            tail_y.append(next_element.value)
            reference = np.array(head_x + tail_x), np.array(head_y + tail_y)
            self.__compare(EVAL_RAW, evaluated, reference)
            head_x.pop(0), head_y.pop(0)
            head_x.append(evaluated.time)
            head_y.append(evaluated.value)
            i += 1

    def __jump_evaluation(self):
        values = []
        jump_values = []
        size = len(self)
        diff = abs(self[0].value - self[1].value)
        i = 1
        while i < size - 1:
            value = diff
            current = self[i]
            diff = abs(current.value - self[i+1].value)
            value += diff
            values.append(value)
            jump_values.append((value, current))
            i += 1
        avg = sum(values) / len(values)
        avg += avg * self.DISTANCE_INTERVAL_PERCENT
        for value, element in jump_values:
            if value >= avg:
                element.potential_flag(EVAL_DISTANCE, 1)
            else:
                element.potential_flag(EVAL_DISTANCE, -1)
            continue

    def evaluate(self):
        print('>>>>> EVALUATION <<<<<')
        print('>>> Raw evaluation')
        self.__raw_evaluation()
        print('>>> Jump evaluation')
        self.__jump_evaluation()


class DataTrainObject(DataObjSet):
    TRAIN_CHANGE_PERCENT = 0.3

    @staticmethod
    def __merge_scores(score_an, score_no, score_all):
        score = score_an + score_no + score_all
        if score_no < 0.45:
            score -= (0.45 - score_no) * 0.08
        if score_an < 0.45:
            score -= (0.45 - score_an) * 0.06
        return 1

    def __calc_score(self):
        size_an, size_no, count_an, count_no = 0, 0, 0, 0
        for element in self:
            if element.label:
                if element.potential > 0:
                    count_an += 1
                size_an += 1
            else:
                if element.potential <= 0:
                    count_no += 1
                size_no += 1
        score_an, score_no = count_an / size_an, count_no / size_no
        score_all = (count_no + count_an) / (size_an + size_no)
        return self.__merge_scores(score_an, score_no, score_all)

    def __change_coefficients(self):
        for idx in range(SIZE_EVAL):
            current = self._coefficients[idx]
            interval = abs(current * self.TRAIN_CHANGE_PERCENT)
            lower, upper = current - interval, current + interval
            self._coefficients[idx] = uniform(lower, upper)

    def train(self, repetition=50):
        print('>>>>> TRAINING <<<<<')
        best_score = -1
        best_coefficients = self.coefficients
        for _ in range(repetition):
            self.__change_coefficients()
            score = self.__calc_score()
            if score > best_score:
                if best_score != -1:
                    print(f'> Better solution for {self.kpi} -- ({score} > {best_score})')
                best_score = score
                best_coefficients = self.coefficients
        self._coefficients = best_coefficients

    def print_result(self):
        result = {}.fromkeys(('anomaly_ok', 'anomaly_ko', 'normal_ok', 'normal_ko'), 0)
        for element in self:
            if element.label:
                key = 'anomaly_ok' if element.potential > 0 else 'anomaly_ko'
            else:
                key = 'normal_ok' if element.potential <= 0 else 'normal_ko'
            result[key] += 1
        print('= Raw result:', result)
        for key in ('anomaly', 'normal'):
            ok = result[f'{key}_ok']
            percent = ok + result[f'{key}_ko']
            percent = ok / percent
            print(f'  {key.capitalize()} success percent', percent)


class DataTestObject(DataObjSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def export(self, file):
        print('Exporting result with KPI', self.kpi)
        for element in self:
            s = element.export_string()
            file.write(s)
