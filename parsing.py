
import csv
import json

from data_objects import DataObj, DataObjContainer, DataTrainObject, DataTestObject, MODEL_PATH


class ModelLoader:
    def __init__(self):
        self._coefficients = self.__get_coefficients()

    @staticmethod
    def __get_coefficients():
        try:
            with open(MODEL_PATH, 'r') as file:
                raw = json.load(file)
                if not isinstance(raw, dict):
                    raise TypeError('The loaded JSON is not a dict')
        except (FileNotFoundError, TypeError) as e:
            print('Exception on loading:', e)
            raw = {}
        return raw

    def __getitem__(self, item):
        return self._coefficients.get(item, [])


class Parser:
    TRAIN_KEYS = ('timestamp', 'value', 'label')
    TEST_KEYS = ('timestamp', 'value')
    KPI_KEY = 'KPI ID'

    __slots__ = ('_dataset', '_target_type', '_limit', '_model_loader')

    def __init__(self, limit=None):
        self._dataset = {}
        self._limit = limit
        self._target_type = DataObjContainer
        self._model_loader = ModelLoader()

    def __checks_keys(self, reader, expected_keys):
        try:
            keys = next(reader)
        except StopIteration:
            raise IndexError('Empty csv file')
        kpi_position = keys.index(self.KPI_KEY)
        positions = tuple(keys.index(key) for key in expected_keys)
        return kpi_position, positions

    def __push_or_init(self, key, data):
        holder = self._dataset.get(key)
        if holder is None:
            if self._limit is not None and len(self._dataset) >= self._limit:
                raise StopIteration
            print('Creating', self._target_type.__name__, 'with KPI', key)
            holder = self._target_type(key, self._model_loader[key])
            self._dataset[key] = holder
        data = DataObj(holder, len(holder), *data)
        holder.add(data)

    def __fill(self, path, expected_keys):
        file = open(path, 'r')
        reader = iter(csv.reader(file))
        kpi_key, positions = self.__checks_keys(reader, expected_keys)
        try:
            while True:
                values = next(reader)
                kpi = values[kpi_key]
                data = [values[idx] for idx in positions]
                self.__push_or_init(kpi, data)
        except StopIteration:
            pass
        file.close()

    def build_train_set(self, path):
        self._dataset = {}
        self._target_type = DataTrainObject
        self.__fill(path, self.TRAIN_KEYS)
        return list(self._dataset.values())

    def build_test_set(self, path):
        self._dataset = {}
        self._target_type = DataTestObject
        self.__fill(path, self.TEST_KEYS)
        return list(self._dataset.values())
