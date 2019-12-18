
from parsing import Parser, MODEL_PATH
from datetime import datetime

import os
import json


def print_general_score(size, general):
    size_an = general['anomaly_ok'] + general['anomaly_ko']
    size_no = general['normal_ok'] + general['normal_ko']
    print('\n=== Overall score over', size, 'dataset')
    print('    Anomaly OK    :', general['anomaly_ok'])
    print('    All Anomalies :', size_an)
    print('    Anomaly score :', general['anomaly_ok'] / size_an)
    print('    Normal OK     :', general['normal_ok'])
    print('    All Normal    :', size_no)
    print('    Normal score  :', general['normal_ok'] / size_no)


def save_result(results):
    print('Saving result in file')
    path = datetime.now().strftime('log_result_%m%d_%H%M%S.json')
    file = open(os.path.join('results', path), 'w')
    json.dump(results, file)
    file.close()


def main():
    p = Parser(limit=None)
    data = p.build_train_set('datasets/train.csv')
    size = len(data)
    coefficients = {}
    general = {}.fromkeys(('anomaly_ok', 'anomaly_ko', 'normal_ok', 'normal_ko'), 0)
    results = {}
    for idx, d in enumerate(data):
        print(f'Dataset {d.kpi} ({idx+1}/{size})')
        d.evaluate()
        # d.train()
        coefficients[d.kpi] = d.coefficients
        result = d.result()
        results[d.kpi] = result
        for k, v in result.items():
            general[k] += v
    print_general_score(len(data), general)
    with open(MODEL_PATH, 'w') as file:
        json.dump(coefficients, file)
    save_result(results)


if __name__ == '__main__':
    main()
