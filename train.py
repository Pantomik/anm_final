
from parsing import Parser
from plot import Plot


def main():
    p = Parser(limit=1)
    data = p.build_train_set('datasets/train.csv')[0]
    data.evaluate()
    # plot = Plot(data, 'test')
    # plot.display_plot(0)
    # plot = Plot(data, 'compare')
    # plot.compare_results(1, [])


if __name__ == '__main__':
    main()
