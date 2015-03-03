# coding: utf-8

import unittest, json, sys
reload(sys)
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')
sys.setdefaultencoding('utf-8')

from server.myapp import app
from uuid import uuid1

class UserTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.book_id = 'afd74cd6-8427-11e4-bb13-642737f58199'
		self.wrong_book_id = 'hehehehehehe'
		self.user_id = '18742513130'

	def get_book_info(self, book_id):
		data = dict(book_id = book_id)
		return self.app.post('/book/getBookInfo', data = data)

	def test_get_book_info(self):
		response = self.get_book_info(self.book_id)
		data = json.loads(response.data)
		assert data['book_id'] == self.book_id and data['bookname'] == \
				u'工程经济学' and data['username'] == u'呵呵' and \
				data['mobile']=='18742513130' and data['qq'] == '86655569'\
				and data['price'] == 236.0

		response = self.get_book_info(self.wrong_book_id)
		assert response.data == 'failed'

	def set_book_info(self, book_info):
		return self.app.post('/book/setBookInfo', data = book_info)

	def test_set_book_info(self):
		new_book_id = str(uuid1())
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

	def set_book_status(self, book_id, status):
		data = dict(book_id = book_id, status = status)
		return self.app.post('/book/setBookStatus', data = data)

	def test_set_book_status(self):
		status = 2
		response = self.set_book_status(self.book_id, status)
		assert response.data = 'success'

		response = self.get_book_info(self.book_id)
		data = json.loads(response.data)
		assert data['status'] = status

	def get_book_by_user(self, user_id):
		data = dict(user_id = user_id)
		return self.app.post('/book/getBooksByUser', data = data)

	def test_get_book_by_user(self):
		response = self.get_book_by_user(self.user_id)
		books = json.loads(response.data)
		for book in books:
			assert book['user_id'] = self.user_id

	def get_book_by_type(self, type):
		data = dict(type = type)
		return self.app.post('/book/getBooksByType', data = data)

	def test_get_book_by_type(self):
		type = 1
		response = self.get_book_by_type(type)
		books = json.loads(response.data)
		for book in books:
			assert book['type'] = type

	def get_book_by_name(self, bookname):
		data = dict(bookname = bookname)
		return self.app.post('/book/getBooksByName', data = data)

	def test_get_book_by_name(self):
		bookname = u'工程经济学'
		books = json.loads(self.get_book_by_name(bookname))
		for book in books:
			assert book['bookname'] = bookname

if __name__ == '__main__':
	unittest.main()