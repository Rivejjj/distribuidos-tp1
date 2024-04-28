import unittest
from common.data_receiver import DataReceiver
from messages.book import Book
from messages.review import Review


class TestUtils(unittest.TestCase):
    base_book = Book('distributed systems', 'description', 'authors', 'image', 'preview_link', 'publisher',"2019", 'info_link', ['category', 'category2'], 'ratings_count')

    base_review = Review('1','distributed systems', '10', '1', 'profile_name', 'helpfulness', '5', 'time', 'summary', 'text')

    def test_parse_book(self):
        data_receiver = DataReceiver()
        book = data_receiver.parse_book('distributed systems,description,authors,image,preview_link,publisher,2019,info_link,category;category2,ratings_count')
        self.assertEqual(book.title, self.base_book.title)
        self.assertEqual(book.description, self.base_book.description)
        self.assertEqual(book.authors, self.base_book.authors)
        self.assertEqual(book.image, self.base_book.image)
        self.assertEqual(book.previewLink, self.base_book.previewLink)
        self.assertEqual(book.publisher, self.base_book.publisher)
        self.assertEqual(book.publishedDate, self.base_book.publishedDate)
        self.assertEqual(book.infoLink, self.base_book.infoLink)
        self.assertEqual(book.categories, self.base_book.categories)
        self.assertEqual(book.ratingsCount, self.base_book.ratingsCount)

    def test_parse_book_raises_value_error(self):
        data_receiver = DataReceiver()
        with self.assertRaises(ValueError) as ctx:
            data_receiver.parse_book('distributed systems')

        self.assertTrue(ValueError, ctx.exception)

    def test_parse_review(self):
        data_receiver = DataReceiver()
        review = data_receiver.parse_review('1,distributed systems,10,1,profile_name,helpfulness,5,time,summary,text')
        self.assertEqual(review.id, self.base_review.id)
        self.assertEqual(review.title, self.base_review.title)
        self.assertEqual(review.price, self.base_review.price)
        self.assertEqual(review.user_id, self.base_review.user_id)
        self.assertEqual(review.profileName, self.base_review.profileName)
        self.assertEqual(review.helpfulness, self.base_review.helpfulness)
        self.assertEqual(review.score, self.base_review.score)
        self.assertEqual(review.time, self.base_review.time)
        self.assertEqual(review.summary, self.base_review.summary)
        self.assertEqual(review.text, self.base_review.text)
