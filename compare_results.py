import difflib
import csv

from utils.parser import split_line

ROUNDING_PRECISION = 5


def compare_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        reader1 = csv.reader(f1)
        reader2 = csv.reader(f2)
        for row1, row2 in zip(reader1, reader2):
            for val1, val2 in zip(row1, row2):
                try:
                    val1 = round(float(val1), ROUNDING_PRECISION)
                    val2 = round(float(val2), ROUNDING_PRECISION)
                except ValueError:
                    pass
                finally:
                    if val1 != val2:
                        print(f'Valores {val1} y {val2} son distintos')
                        return

    print(f'Archivos {file1} y {file2} son iguales')


def sort_file(path, write_path):
    with open(path, 'r') as f, open(write_path, 'w') as d:
        reader = csv.reader(f)
        rows = list(reader)
        rows.sort(key=lambda x: split_line(x[0]))

        writer = csv.writer(d)
        writer.writerows(rows)


def main():
    sort_file('data/query/query1.csv', 'data/query_result/query1.csv')
    sort_file('data/query/query2.csv', 'data/query_result/query2.csv')
    sort_file('data/query/query3.csv', 'data/query_result/query3.csv')
    sort_file('data/query/query4.csv', 'data/query_result/query4.csv')
    sort_file('data/query/query5.csv', 'data/query_result/query5.csv')
    compare_files('data/query_result/query1.csv',
                  'data/kaggle_results/query_1_kaggle.csv')
    compare_files('data/query_result/query2.csv',
                  'data/kaggle_results/query_2_kaggle.csv')
    compare_files('data/query_result/query3.csv',
                  'data/kaggle_results/query_3_kaggle.csv')
    compare_files('data/query_result/query4.csv',
                  'data/kaggle_results/query_4_kaggle.csv')
    compare_files(
        'data/query_result/query5.csv', 'data/kaggle_results/query_5_kaggle.csv')


if __name__ == '__main__':
    main()
