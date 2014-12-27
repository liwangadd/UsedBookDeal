# coding: utf-8

import unittest, json, sys
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')

from server.myapp import app

class UserTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()

	def test_root_url(self):
		response = self.app.get('/')
		assert 'hello' == response.data

	def login(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/login', data=data)

	def test_login(self):
		response = self.login('18840822454', '123')
		assert response.data == 'success'
		response = self.login('18840822453', '123')
		assert response.data == 'failed'
		response = self.login('18840822454', '1234')
		assert response.data == 'failed'

	def register(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/register', data=data)

	# def test_register(self):
	# 	response = self.register('13784397168', '123456')
	# 	assert response.data == 'success'
	# 	response = self.register('13784397168', '123456')
	# 	assert response.data == 'failed'

	def set_user_info(self, **userinfo):
		return self.app.post('/user/setUserInfo', data=userinfo)

	def get_user_info(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getUserInfo', data=data)

	def test_set_user_info(self):

		response = self.set_user_info(user_id='18840822453', username='hehe')
		assert response.data == 'failed'

		response = self.set_user_info(user_id='13784397168', username='hehe',
			mobile='13784397168')
		assert response.data == 'success'

		response = self.get_user_info('13784397168')
		data = json.loads(response.data)
		assert data['user_id'] == '13784397168' and data['username'] == 'hehe'\
				and data['mobile'] == '13784397168'

		response = self.get_user_info('13784397167')
		assert response.data == 'failed'

	def get_user_message(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getMessages', data=data)

	def test_get_messages(self):
		# calling method wish wrong user_id will return no 'failed' but empty
		# list of messages
		response = self.get_user_message('13784397167')
		data = json.loads(response.data)
		assert len(data['messages']) == 0

		response = self.get_user_message('18742513130')
		data = json.loads(response.data)
		for message in data['messages']:
			assert message['user_id'] == '18742513130'
			print message

if __name__ == '__main__':
	unittest.main()