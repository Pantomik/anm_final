
from scipy.interpolate import interp1d
import numpy as np


class DataObj:
    __slots__ = ('_parent', '_idx', '_time', '_value', '_label')

    def __init__(self, parent, idx: int, timestamp, value, label=None):
        assert isinstance(parent, DataObjSet)
        self._parent = parent
        self._idx = idx
        self._time = int(timestamp)
        self._value = float(value)
        self._label = label
        if label is not None:
            self._label = int(label) == 1

    def __repr__(self):
        label = ''
        if self._label is not None:
            label = ' ' + str(self._label)
        return f'<{self.kpi}> {self.time}: {self.value} {label}'

    @property
    def time(self):
        return self._time

    @property
    def value(self):
        return self._value

    @property
    def kpi(self):
        return self._parent.kpi

    def expected_label(self, expected: bool):
        pass


class DataObjContainer:
    def __init__(self, kpi):
        self._keys = None
        self._elements = {}
        self._kpi = kpi

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._average_threshold = 0

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

    def __compare(self, evaluated, reference):
        x, y = reference
        cubic = interp1d(x, y, kind='cubic')
        expected = cubic(evaluated.time)
        diff = abs(evaluated.value - expected)
        print(diff)

    def evaluate(self):
        self._average_threshold = 0
        size = len(self._elements) - self.IGNORE_START
        i = self.IGNORE_START
        (head_x, head_y), (tail_x, tail_y) = self.__start()
        next_value = self.IGNORE_START * 2 + 1
        while i < size:
            tail_x.pop(0), tail_y.pop(0)
            evaluated, next_element = self[i], self[next_value + i]
            tail_x.append(next_element.time)
            tail_y.append(next_element.value)
            reference = np.array(head_x + tail_x), np.array(head_y + tail_y)
            self.__compare(evaluated, reference)
            head_x.pop(0), head_y.pop(0)
            head_x.append(evaluated.time)
            head_y.append(evaluated.value)
            i += 1


class DataTrainObject(DataObjSet):
    pass


class DataTestObject(DataObjSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._failed = []
