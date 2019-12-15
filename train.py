
from parsing import Parser, MODEL_PATH
from plot import Plot

import json


def main():
    p = Parser(limit=2)
    data = p.build_train_set('datasets/train.csv')
    size = len(data)
    """plot = Plot(data, 'train')
    skip = ()
    for i in range(size):
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
    for idx, d in enumerate(data):
        print(f'Dataset {d.kpi} ({idx+1}/{size})')
        d.evaluate()
        d.train()
        coefficients[d.kpi] = d.coefficients
        d.print_result()
    with open(MODEL_PATH, 'w') as file:
        json.dump(coefficients, file)


if __name__ == '__main__':
    main()
