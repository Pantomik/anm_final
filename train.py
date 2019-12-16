
from parsing import Parser, MODEL_PATH
from plot import Plot

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


def main():
    p = Parser(limit=None)
    data = p.build_train_set('datasets/train.csv')
    size = len(data)
    plot = Plot(data, 'train')
    skip = ()
    """for i in range(size):
        if i in skip:
            print('% Skipped', i)
            continue
        print('Dataset', i)
        plot.display_plot(i)
    return"""
    # plot = Plot(data, 'train')
    # plot.display_plot(0)
    # plot = Plot(data, 'compare')
    # plot.compare_results(1, [])
    coefficients = {}
    general = {}.fromkeys(('anomaly_ok', 'anomaly_ko', 'normal_ok', 'normal_ko'), 0)
    for idx, d in enumerate(data):
        print(f'Dataset {d.kpi} ({idx+1}/{size})')
        d.evaluate()
        d.train()
        coefficients[d.kpi] = d.coefficients
        result = d.result()
        for k, v in result.items():
            general[k] += v
        # plot.display_plot(idx)
    print_general_score(len(data), general)
    with open(MODEL_PATH, 'w') as file:
        json.dump(coefficients, file)


if __name__ == '__main__':
    main()
