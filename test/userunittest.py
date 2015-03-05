# coding: utf-8

import unittest, json, sys
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')

from server.myapp import app

class UserTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.user_id = '18742513130'
		self.password = '1234'

	def test_root_url(self):
		response = self.app.get('/')
		assert 'hello' == response.data

	def login(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/login', data=data)

	def test_login(self):
		response = self.login(self.user_id, self.password)
		assert response.data == 'success'
		response = self.login(self.user_id, '123')
		assert response.data == 'wrong_password'
		response = self.login('wrong_user_id', '1234')
		assert response.data == 'wrong_user_id'

	def register(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/register', data=data)

	def test_register(self):
		response = self.register('18840822453', '123456')
		assert response.data == 'success'
		response = self.register(self.user_id, '123456')
		assert response.data == 'conflict_user_id'

	def get_user_info(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getUserInfo', data=data)

	def test_get_user_info(self):
		response = self.get_user_info(self.user_id)
		user = json.loads(response.data)
		assert user['user_id'] == self.user_id and user['password'] == \
				self.password and user['mobile'] == self.user_id

		response = self.get_user_info('13784397167')
		assert response.data == 'failed'

	def set_user_info(self, **userinfo):
		return self.app.post('/user/setUserInfo', data=userinfo)

	def test_set_user_info(self):

		response = self.set_user_info(user_id='wrong_user_id', username='hehe')
		assert response.data == 'failed'

		response = self.set_user_info(user_id='13784397168', username='hehe',
			mobile='13784397168')
		assert response.data == 'success'

		response = self.get_user_info('13784397168')
		data = json.loads(response.data)
		assert data['user_id'] == '13784397168' and data['username'] == 'hehe'\
				and data['mobile'] == '13784397168'

	def get_user_message(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getMessages', data=data)

	def test_get_messages(self):
		# calling method wish wrong user_id will return no 'failed' but empty
		# list of messages
		response = self.get_user_message('13784397167')
		data = json.loads(response.data)
		assert len(data['messages']) == 0

		response = self.get_user_message(self.user_id)
		data = json.loads(response.data)
		messages = data['messages']
		assert len(messages) != 0
		for message in messages:
			assert message['user_id'] == self.user_id

	def clear_messages_by_user(self, user_id):
		data = dict(user_id = user_id)
		return self.app.post('/user/clearMessages', data = data)

	def test_clear_messages(self):
		response = self.clear_messages_by_user(self.user_id)
		assert response.data == 'success'

		response = self.get_user_message(self.user_id)
		data = json.loads(response.data)
		messages = data['messages']
		assert len(messages) == 0

if __name__ == '__main__':
	unittest.main()