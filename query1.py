
def filter_by_category(book, category):
	if "Computers" in book.categories:
		return book
	
def filter_by_year(book, min_year, max_year):
	if min_year < book.publishedDate < max_year:
		return book
			
def filter_by_title(book, title):
	if title in book.title:
		return book

