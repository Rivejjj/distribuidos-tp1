import csv
ROUNDING_PRECISION = 5


def compare_files_with_rounding(file1, file2):
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
        rows.sort()

        writer = csv.writer(d)
        writer.writerows(rows)


def main():
    for i in range(1, 6):
        sort_file(f'data/0/query/query{i}.csv',
                  f'data/query_result/0/query{i}.csv')
        sort_file(f'data/kaggle_results/query{i}_reduced.csv',
                  f'data/kaggle_results/query{i}_reduced_sorted.csv')
        compare_files_with_rounding(f'data/query_result/0/query{i}.csv',
                                    f'data/kaggle_results/query{i}_reduced_sorted.csv')


if __name__ == '__main__':
    main()
