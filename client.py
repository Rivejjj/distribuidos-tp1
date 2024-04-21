

BOOKS_DATA_PATH = "books_data.csv"

class Csv:
	def __init__(self):
		self.col_idx = 0
		self.columns = {}
		self.row_idx = 0
		self.rows = {}


	def read_csv(self, path):
		with open(path, 'r', encoding="utf8") as file:
			line = file.readline()
			line = line.strip('\n')
			for i in line.split(','):
				self.columns[i] = self.col_idx
				self.col_idx +=1 

			while line:
				line = file.readline()
				line = line.strip('\n')
				row = line.split(',')
				self.rows[self.row_idx] = row


def read_csv(path):
	csv = Csv()
	csv.read_csv(path)
	return csv


def main():
	csv = read_csv(BOOKS_DATA_PATH)
	print(csv.rows.values())


main()
	