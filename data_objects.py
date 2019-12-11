
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

    @property
    def label(self):
        return self._label

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

    def __sub(self, start=0):
        x, y = [], []
        for i in range(self.IGNORE_START):
            element = self[start + i]
            x.append(element.time)
            y.append(element.value)
        return x, y

    def evaluate(self):
        size = len(self._elements) - self.IGNORE_START
        x, y = [], []
        for idx in range(self.IGNORE_START * 2 + 1):
            element = self[idx]
            x.append(element.time)
            y.append(element.value)
        i = self.IGNORE_START
        while i < size:
            # interp1d(np.array(head_x + ))
            i += 1


class DataTrainObject(DataObjSet):
    pass


class DataTestObject(DataObjSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._failed = []
