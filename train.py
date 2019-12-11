
from parsing import Parser


def main():
    p = Parser(limit=1)
    data = p.build_train_set('datasets/train.csv')[0]
    data.evaluate()


if __name__ == '__main__':
    main()
