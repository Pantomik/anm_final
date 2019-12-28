
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

import numpy as np


MODEL_PATH = 'models.json'

EVAL_KEYS = (
    'coef_jump_up',
    'coef_jump_down',
    'coef_spread',
    'coef_extreme_up',
    'coef_extreme_down',
    'coef_simple_bands',
    'param_jump_up',
    'param_jump_down',
    'param_extreme_up',
    'param_extreme_down',
)

(EVAL_JUMP_UP, EVAL_JUMP_DOWN, EVAL_SPREAD, EVAL_EXTREME_UP, EVAL_EXTREME_DOWN,
 EVAL_SIMPLE_BANDS,
 PARAM_JUMP_UP, PARAM_JUMP_DOWN, PARAM_EXTREME_UP, PARAM_EXTREME_DOWN) = EVAL_KEYS


def inside_value(value, lower, upper):
    if value > upper:
        return upper
    if value < lower:
        return lower
    return value


def calc_potential(value, start, end):
    if (not start < value < end) and (not start > value > end):
        return -0.1
    full_dist = abs(start - end)
    if full_dist == 0.0:
        return 0.0
    dist = abs(start - value)
    return dist / full_dist


class DataObj:
    POTENTIAL_SPREADING = 10

    __slots__ = ('_parent', '_idx', '_time', '_value', '_label', '_potential')

    def __init__(self, parent, idx: int, timestamp, value, label=None):
        assert isinstance(parent, DataObjSet)
        self._parent = parent
        self._idx = idx
        self._time = int(timestamp)
        self._value = float(value)
        self._potential = {}
        self._label = label
        if label is not None:
            self._label = int(label) == 1

    def __repr__(self):
        label = ''
        if self._label is not None:
            label = ' ' + str(self._label)
        return f'<{self.kpi}> {self.time}: {self.value} {label}'

    def __lt__(self, other):
        if not isinstance(other, DataObj):
            raise TypeError
        return self.value < other.value

    @property
    def potential(self):
        coefficients = self._parent.coefficients
        div = 0.0
        ret = 0.0
        for k, v in self._potential.items():
            if k in coefficients.keys():
                coef = coefficients[k]
                if coef is None:
                    coef = 0.0
            else:
                self._parent.reset_coefficient(k)
                coef = 1.0
            ret += v * coef
            div += coef
        if div == 0.0:
            div = 1.0
        return ret / div

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

    def potential_flag(self, key: str, modifier: float, recursive=True):
        potential = self._potential.get(key, 0.0) + modifier
        self._potential[key] = potential
        if recursive:
            for pad in range(1, self.POTENTIAL_SPREADING):
                pad += 2
                new = modifier / (pad * 0.35)
                try:
                    self._parent[self._idx - int(pad)].potential_flag(EVAL_SPREAD, new, False)
                except IndexError:
                    pass
                try:
                    self._parent[self._idx + int(pad)].potential_flag(EVAL_SPREAD, new, False)
                except IndexError:
                    pass


class DataObjContainer:
    def __init__(self, kpi, coefficients):
        assert isinstance(coefficients, dict)
        self._keys = None
        self._elements = {}
        self._kpi = kpi
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

    def reset_coefficient(self, key):
        if key == EVAL_SPREAD:
            self._coefficients[key] = 1.0
        else:
            self._coefficients[key] = 1.0

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
    BANDS_SIZE = 160

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_values = []
        self._jump_values = []
        self._bands = []

    def __calc_mean_and_std(self, start, end, mean):
        size = end - start
        std = 0
        for i in range(start, end):
            std += (self._raw_values[i][0] - mean) ** 2
        std = (std / size) ** 0.5
        return std

    def __get_oldest_value(self, i):
        if i < self.BANDS_SIZE:
            return 0
        i = i - self.BANDS_SIZE
        return inside_value(self[i].value, *self._bands[i])

    def __plot(self, *more):
        print('##### Plot #####')
        size = len(self)
        timestamps, values, colors, upper, lower = [], [], [], [], []
        for i in range(size):
            element = self[i]
            timestamps.append(element.time)
            values.append(element.value)
            colors.append('r' if element.label else 'b')
            up, low = self._bands[i]
            upper.append(up)
            lower.append(low)
        lines = [((x0, y0), (x1, y1)) for x0, y0, x1, y1 in zip(timestamps[:-1], values[:-1], timestamps[1:], values[1:])]
        _, ax = plt.subplots(1)
        ax.plot(timestamps, lower, timestamps, upper)
        colored_lines = LineCollection(lines, colors=colors, linewidths=(1,))
        for data in more:
            ax.plot(timestamps, data)
        ax.add_collection(colored_lines)
        ax.autoscale_view()
        plt.yticks([])
        plt.xticks([])
        plt.show()

    def __plot2(self):
        values = sorted(self._jump_values)
        y, c = [], []
        for value, element in values:
            y.append(value)
            c.append('r' if element.label else 'b')
        lines = [((idx, y0), (idx+1, y1)) for idx, (y0, y1) in enumerate(zip(y[:-1], y[1:]))]
        _, ax = plt.subplots(1)
        ax.add_collection(LineCollection(lines, colors=c, linewidths=(2,)))
        ax.autoscale_view()
        plt.yticks(np.arange(min(y), max(y), sum(y) / (len(y))))
        plt.xticks([])
        plt.show()

    def __setup(self):
        last_value, last_jump, last_element = 0, 0, 0
        sum_value = 0
        for i in range(len(self)):
            # Pre operations
            element = self[i]
            value = element.value
            jump = abs(last_value - value)
            sum_value -= self.__get_oldest_value(i)
            start, div = 0, i if i != 0 else 1
            if i >= self.BANDS_SIZE:
                start, div = (i + 1) - self.BANDS_SIZE, self.BANDS_SIZE
            mean = sum_value / div
            # Operations
            self._raw_values.append((value, element))
            std = self.__calc_mean_and_std(start, i + 1, mean) * 2.3
            lower, upper = mean - std, mean + std
            self._bands.append((lower, upper))
            if i > 2:
                self._jump_values.append((last_jump + jump, last_element))
            # Post operations
            sum_value += inside_value(value, lower, upper)
            last_jump = jump
            last_value = value
            last_element = element
        # self.__plot2()
        self.__plot()

    def _ask_for_param(self, key):
        raise NotImplementedError

    @staticmethod
    def __order_as_cumulative_func(values):
        x = sorted(values)
        incr = 1 / len(values)
        y = [incr * times for times in range(1, len(values) + 1)]
        return x, y

    def __jump_evaluation(self):
        up = self._ask_for_param(PARAM_JUMP_UP)
        down = self._ask_for_param(PARAM_JUMP_DOWN)
        pure = [v for v, _ in self._jump_values]
        max_jump, min_jump = max(pure), min(pure)
        for jump, element in self._jump_values:
            if up is not None:
                element.potential_flag(EVAL_JUMP_UP, calc_potential(jump, up, min_jump))
            if down is not None:
                element.potential_flag(EVAL_JUMP_DOWN, calc_potential(jump, down, max_jump))

    def __extreme_evaluation(self):
        up = self._ask_for_param(PARAM_EXTREME_UP)
        down = self._ask_for_param(PARAM_EXTREME_DOWN)
        pure = [v for v, _ in self._raw_values]
        min_extreme, max_extreme = min(pure), max(pure)
        for element in self:
            value = element.value
            if up is not None:
                element.potential_flag(EVAL_EXTREME_UP, calc_potential(value, up, min_extreme))
            if down is not None:
                element.potential_flag(EVAL_EXTREME_DOWN, calc_potential(value, down, max_extreme))

    def __bands_evaluation(self):
        i, stop = self.BANDS_SIZE // 2, len(self)
        while i < stop:
            element = self[i]
            value = element.value
            lower, upper = self._bands[i]
            if lower <= value <= upper:
                element.potential_flag(EVAL_SIMPLE_BANDS, -0.3)
            else:
                std = (upper - lower)
                if value < lower:
                    potential = calc_potential(value, lower - std, lower)
                else:  # value > upper
                    potential = calc_potential(value, upper, upper + std)
                element.potential_flag(EVAL_SIMPLE_BANDS, potential)
            i += 1

    def evaluate(self):
        print('>>>>> EVALUATION <<<<<')
        print('> Setting up')
        self.__setup()
        # print('>>> Jump evaluation')
        # self.__jump_evaluation()
        # print('>>> Extreme evaluation')
        # self.__extreme_evaluation()
        # print('>>> Bands evaluation')
        # self.__bands_evaluation()


class DataTrainObject(DataObjSet):
    PARAM_CALC = {
        PARAM_JUMP_UP: ('_jump_values', False),
        PARAM_JUMP_DOWN: ('_jump_values', True),
        PARAM_EXTREME_UP: ('_raw_values', False),
        PARAM_EXTREME_DOWN: ('_raw_values', True),
    }

    TRAIN_CHANGE_PERCENT = 1.5
    MAXIMUM_TRY_SCOPE = 30

    @staticmethod
    def __merge_scores(score_an, score_no, score_all):
        score = score_an + score_no + score_all
        if score_no < 0.45:
            score -= (0.45 - score_no) * 0.18
        if score_an < 0.45:
            score -= (0.45 - score_an) * 0.06
            if score_no < 0.3:
                score -= 0.1
        return score

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

    def _ask_for_param(self, key):
        var, from_bottom = self.PARAM_CALC[key]
        var = sorted(getattr(self, var), reverse=from_bottom)
        threshold = None
        i, size = 0, len(var)
        while i < size:
            j, count = 0, 0
            while i + j < size:
                if var[i + j][1].label:
                    count += 1
                    if count >= j / 2:
                        threshold = var[i + j][0]
                        i += j
                        break
                elif j >= self.MAXIMUM_TRY_SCOPE:
                    break
                j += 1
            if j >= self.MAXIMUM_TRY_SCOPE:
                break
            i += 1
        self._coefficients[key] = threshold
        return threshold

    def __improve_coef(self, key, best_score):
        incr = 1
        while True:
            if incr <= (10 ** -8):
                break
            origin = self._coefficients[key]
            more, less = origin + incr, origin - incr
            self._coefficients[key] = more
            more_score = self.__calc_score()
            self._coefficients[key] = less
            less_score = self.__calc_score()
            evaluation = ((best_score, 1, origin), (more_score, 0, more), (less_score, 0, less))
            score, _, self._coefficients[key] = max(evaluation)
            if score != best_score:
                print('> Better score found', score)
                best_score = score
                continue
            incr = incr / 10
        return best_score

    def train(self):
        print('>>>>> TRAINING <<<<<')
        best_score = self.__calc_score()
        print('>> Base score', best_score)
        keys = set()
        for key in self._coefficients.keys():
            if key[:5] != 'coef_':
                continue
            keys.add(key)
        for key in keys:
            if self._coefficients[key] is None:
                print('>> Key', key, 'is fixed...')
                continue
            print('>> Train key', key)
            best_score = self.__improve_coef(key, best_score)
        return best_score

    def result(self):
        result = {}.fromkeys(('anomaly_ok', 'anomaly_ko', 'normal_ok', 'normal_ko'), 0)
        for element in self:
            if element.label:
                key = 'anomaly_ok' if element.potential > 0 else 'anomaly_ko'
            else:
                key = 'normal_ok' if element.potential <= 0 else 'normal_ko'
            result[key] += 1
        score = 0.0
        print('= Raw result:', result)
        for key in ('anomaly', 'normal'):
            ok = result[f'{key}_ok']
            percent = ok + result[f'{key}_ko']
            percent = ok / percent
            score += percent
            print(f'  {key.capitalize()} success percent \t', percent)
        score = score / 2 * 100
        print('  General score\t\t\t {:0.2f}\n'.format(score))
        return result


class DataTestObject(DataObjSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _ask_for_param(self, key):
        return self._coefficients[key]

    def export(self, file):
        print('Exporting result with KPI', self.kpi)
        for element in self:
            s = element.export_string()
            file.write(s)
