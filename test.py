
from parsing import Parser


def main():
    p = Parser()
    data = p.build_test_set('datasets/test.csv')
    file = open('output.csv', 'w')
    file.write('KPI ID,timestamp,predict\n')
    for d in data:
        d.evaluate()
        d.export(file)
    file.close()


if __name__ == '__main__':
    main()
