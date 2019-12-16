
from parsing import Parser

def main():
    p = Parser()
    data = p.build_train_set('datasets/train.csv')

if __name__ == '__main__':
    main()
