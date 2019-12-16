
from parsing import Parser


def main():
    p = Parser()
    data = p.build_test_set('datasets/test.csv')
    file = open('output.csv', 'w')
    file.write('KPI ID,timestamp,predict\n')
    size = len(data)
    for idx, d in enumerate(data):
        print(f'Dataset {d.kpi} ({idx+1}/{size})')
        d.evaluate()
        d.export(file)
    file.close()


if __name__ == '__main__':
    main()
