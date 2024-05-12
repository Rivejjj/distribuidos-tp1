import difflib
import csv

ROUNDING_PRECISION = 5


def compare_files(file1, file2):
    diff_str = ''
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        diff = difflib.context_diff(
            f1.readlines(),
            f2.readlines(),
            fromfile=file1,
            tofile=file2
        )

        diff_str = ''.join(diff)

    if diff_str:
        print(diff_str)
    else:
        print(f'Files {file1} and {file2} are identical')


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
                        print(f'Files {file1} and {file2} are different')
                        print(f'Values {val1} and {val2} are different')
                        return

    print(f'Files {file1} and {file2} are identical')


def sort_file(path, write_path):
    with open(path, 'r') as f, open(write_path, 'w') as d:
        reader = csv.reader(f)
        rows = list(reader)
        rows.sort(key=lambda x: x[0])

        writer = csv.writer(d)
        writer.writerows(rows)


def main():
    # sort_file('tests/test_results.csv', 'tests/test_results_sorted.csv')
    for i in range(1, 2):
        sort_file(f'query/query{i}.csv', f'query_result/query{i}.csv')


if __name__ == '__main__':
    main()
