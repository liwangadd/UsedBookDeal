# coding: utf-8

import unittest, json, sys
reload(sys)
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')
sys.setdefaultencoding('utf-8')

from server.myapp import app

class WishTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.wish_id = '63e14b24-c85b-11e4-b073-00163e003879'
		self.user_id = '18640934580'

	def list_wishes(self, page, pagesize, wishtype):
		data = dict(page = page, pagesize = pagesize, type = wishtype)
		return self.app.post('/wish/listWishes', data = data)

	def test_list_wishes(self):
		page = 1; pagesize = 5; wishtype = 1
		response = self.list_wishes(page, pagesize, wishtype)
		data = json.loads(response.data)
		wishes = data['wishes']
		assert len(wishes) <= 5
		for wish in wishes:
			assert wish['type'] == wishtype

	def get_wish_info(self, wish_id):
		data = dict(wish_id = wish_id)
		return self.app.post('/wish/getWishInfo', data = data)

	def test_get_wish_info(self):
		response = self.get_wish_info(self.wish_id)
		wish = json.loads(response.data)
		assert wish['wish_id'] == self.wish_id

		response = self.get_wish_info('wrong_wish_id')
		assert response.data == 'failed'

	def set_wish_info(self, **wish_info):
		return self.app.post('/wish/setWishInfo', data = wish_info)

	def test_set_wish_info(self):
		wish_info = {}
		wish_info['bookname'] = 'erp'
		wish_info['user_id'] = self.user_id
		wish_info['type'] = 1
		response = self.set_wish_info(**wish_info)
		assert response.data == 'success'

		response = self.set_wish_info(wish_id = self.wish_id, user_id = self.user_id, type = 2)
		assert response.data == 'success'

		response = self.get_wish_info(self.wish_id)
		wish = json.loads(response.data)
		assert wish['type'] == 2

		response = self.set_wish_info(wish_id = 'wrong_wish_id', type = 2)
		assert response.data == 'failed'

		wish_info['user_id'] = '18840823333'
		wish_info['reward'] = '0'
		wish_info['price'] = 5
		del wish_info['type']
		response = self.set_wish_info(**wish_info)
		assert response.data == 'success'

	def list_wishes_v1_5(self, type_v1_5, university, order_by, page,pagesize):
		data = dict(type_v1_5 = type_v1_5, university = university,
				order_by = order_by, page = page, pagesize = pagesize)
		return self.app.post('/wish/listWishesV1_5', data = data)

	def test_list_wishes_v1_5(self):
		type_v1_5 = 0
		university = u'大连理工大学'
		order_by = 'gender'
		page = 1; pagesize = 5;
		response = self.list_wishes_v1_5(type_v1_5, university, order_by,
				page, pagesize)
		# print response.data
		data = json.loads(response.data)
		wishes = data['wishes']
		assert len(wishes) <= 5 and len(wishes) > 0
		# for wish in wishes:
			# assert wish['type'] == wishtype

	def set_wish_status(self, wish_id, user_id, username, status):
		data = dict(wish_id = wish_id, user_id = user_id, username = username, status = status)
		return self.app.post('/wish/setWishStatus', data = data)

	def test_set_wish_status(self):
		username = u'呵呵'
		status = 1
		response = self.set_wish_status(self.wish_id, self.user_id, username, status)
		assert response.data == 'success'

		response = self.get_wish_info(self.wish_id)
		wish = json.loads(response.data)
		assert wish['status'] == status

	def wish_clicked(self, wish_id):
		data = dict(wish_id = wish_id)
		return self.app.post('/wish/wishClicked', data = data)

	def test_wish_clicked(self):
		response = self.get_wish_info(self.wish_id)
		wish = json.loads(response.data)
		old_clicks = wish['clicks']

		response = self.wish_clicked(self.wish_id)
		assert response.data == 'success'

		response = self.get_wish_info(self.wish_id)
		wish = json.loads(response.data)
		new_clicks = wish['clicks']
		assert old_clicks + 1 == new_clicks

if __name__ == '__main__':
	unittest.main()