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
		self.book_id = '2270d7ba-7f7f-11e4-8b3b-642737f58199'
		self.wrong_book_id = 'hehehehehehe'
		self.user_id = '18840822454'

	def get_book_info(self, book_id):
		data = dict(book_id = book_id)
		return self.app.post('/book/getBookInfo', data = data)

	def test_get_book_info(self):
		response = self.get_book_info(self.book_id)
		data = json.loads(response.data)
		assert data['book_id'] == self.book_id and data['bookname']==u'数据库'\
				and data['username']==u'呵呵'and data['mobile']=='18742513130'\
				and data['qq'] == '123' and data['price'] == 250

		response = self.get_book_info(self.wrong_book_id)
		assert response.data == 'failed'

	def set_book_info(self, book_info):
		return self.app.post('/book/setBookInfo', data = book_info)

	def test_set_book_info(self):
		new_book_id = str(uuid1())
		book_info = {}
		# book_info['book_id'] = new_book_id
		book_info['bookname'] = u'计算机网络'
		book_info['user_id'] = self.user_id
		book_info['type'] = 1
		book_info['status'] = 0
		book_info['price'] = 20.73
		response = self.set_book_info(book_info)
		assert response.data == 'success'

if __name__ == '__main__':
	unittest.main()