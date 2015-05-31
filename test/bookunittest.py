# coding: utf-8

import unittest, json, sys
reload(sys)
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')
sys.setdefaultencoding('utf-8')

from server.myapp import app

class BookTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.book_id = '47e3a7c0-c3ef-11e4-b073-00163e003879'
		self.wrong_book_id = 'hehehehehehe'
		self.user_id = '18840823333'

	def get_book_info(self, book_id):
		data = dict(book_id = book_id)
		return self.app.post('/book/getBookInfo', data = data)

	def test_get_book_info(self):
		response = self.get_book_info(self.book_id)
		data = json.loads(response.data)
		assert data['book_id'] == self.book_id
		assert data['bookname'] == u'C++语言程序设计'
		assert data['username'] == u'Neo'
		assert data['mobile'] == '13998636028'
		assert data['qq'] == ''
		assert data['price'] == 4

		response = self.get_book_info(self.wrong_book_id)
		assert response.data == 'failed'

	def set_book_info(self, book_info):
		return self.app.post('/book/setBookInfo', data = book_info)

	def test_set_book_info(self):
		book_info = {}
		# book_info['book_id'] = new_book_id
		book_info['bookname'] = u'erp'
		book_info['user_id'] = self.user_id
		book_info['audience'] = u'学霸'
		book_info['type'] = 1
		book_info['status'] = 0
		book_info['price'] = 20.73
		response = self.set_book_info(book_info)
		assert response.data == 'success'

		book_info['bookname'] = 'ERP'
		book_info['user_id'] = self.user_id
		book_info['audience_v1_5'] = u'学霸'
		book_info['type_v1_5'] = 1
		book_info['status'] = 0
		book_info['price'] = 10
		book_info['original_price'] = 100
		response = self.set_book_info(book_info)
		assert response.data == 'success'

		book_info['book_id'] = 'wrong_book_id'
		response = self.set_book_info(book_info)
		assert response.data == 'failed'

	def set_book_status(self, book_id, status):
		data = dict(book_id = book_id, status = status)
		return self.app.post('/book/setBookStatus', data = data)

	def test_set_book_status(self):
		status = 1
		response = self.set_book_status(self.book_id, status)
		assert response.data == 'success'

		response = self.get_book_info(self.book_id)
		data = json.loads(response.data)
		assert data['status'] == status

	def get_book_by_user(self, user_id):
		data = dict(user_id = user_id)
		return self.app.post('/book/getBooksByUser', data = data)

	def test_get_book_by_user(self):
		response = self.get_book_by_user(self.user_id)
		data = json.loads(response.data)
		books = data['books']
		for book in books:
			assert book['user_id'] == self.user_id

	def get_book_by_type(self, type, page, pagesize):
		data = dict(type = type, page = page, pagesize = pagesize)
		return self.app.post('/book/getBooksByType', data = data)

	def test_get_book_by_type(self):
		type = 1
		page = 1
		pagesize = 1
		response = self.get_book_by_type(type, page, pagesize)
		data = json.loads(response.data)
		books = data['books']
		for book in books:
			assert book.get('price') != None

	def get_book_by_type_v1_5(self, type_v1_5, university, audience_v1_5,
			order_by, page, pagesize):
		data = dict(type_v1_5 = type_v1_5, university = university,page = page,
				pagesize = pagesize, audience_v1_5 = audience_v1_5,
				order_by = order_by)
		return self.app.post('/book/getBooksByTypeV1_5', data = data)

	def test_get_book_by_type_v1_5(self):
		type_v1_5 = 1
		university = u'大连理工大学'
		order_by = 'added_time'
		audience_v1_5 = 'null'
		page = 1
		pagesize = 5
		response = self.get_book_by_type_v1_5(type_v1_5, university,
				audience_v1_5, order_by, page, pagesize)
		data = json.loads(response.data)
		books = data['books']
		for book in books:
			assert book['university'] == u'大连理工大学'

		order_by = 'gender'
		response = self.get_book_by_type_v1_5(type_v1_5, university,
				audience_v1_5, order_by, page, pagesize)
		data = json.loads(response.data)
		books = data['books']
		assert len(books) == 0

	def get_recommended_books(self, page, pagesize):
		data = dict(page = page, pagesize = pagesize)
		return self.app.post('/book/getRecommendedBooks', data = data)

	def test_get_recommended_books(self):
		page = 1; pagesize = 5
		response = self.get_recommended_books(page, pagesize)
		data = json.loads(response.data)
		books = data['books']
		assert len(books) > 0 and len(books) <= 5

	def get_book_by_name(self, bookname):
		data = dict(bookname = bookname)
		return self.app.post('/book/getBooksByName', data = data)

	def test_get_book_by_name(self):
		bookname = u'工程经济学'
		response = self.get_book_by_name(bookname)
		data = json.loads(response.data)
		books = data['books']
		for book in books:
			assert book['bookname'] == bookname

	def get_similar_name(self, bookname, limit):
		data = dict(bookname = bookname, limit = limit)
		return self.app.post('/book/getSimilarBookname', data = data)

	def test_get_similar_name(self):
		bookname = u'erp'
		response = self.get_similar_name(bookname, 2)
		data = json.loads(response.data)
		booknames = data['booknames']
		for name in booknames:
			print name

	# def search_book(self, keyword, page, pagesize):
	# 	data = dict(keyword = keyword, page = page, pagesize = pagesize)
	# 	return self.app.post('/book/searchBook', data = data)

	# def test_search_book(self):
	# 	keyword = '工程经济'
	# 	page = 1
	# 	pagesize = 1
	# 	response = self.search_book(keyword, page, pagesize)
	# 	data = json.loads(response.data)
	# 	books = data['books']
	# 	for book in books:
	# 		print book['bookname']
	# 		assert book['bookname'] == u'工程经济学'

if __name__ == '__main__':
	unittest.main()