# coding: utf-8

import unittest, json, sys
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')

from server.myapp import app

class UserTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.user_id = '18840823333'
		self.password = '123456'

	def test_root_url(self):
		response = self.app.get('/')
		assert 'hello, world!' == response.data

	def register(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/register', data=data)

	def test_register(self):
		# response = self.register(self.user_id, self.password)
		# assert response.data == 'success'
		response = self.register('18840824301', '123456')
		assert response.data == 'conflict_user_id'

	def login(self, user_id, password):
		data = dict(user_id=user_id, password=password)
		return self.app.post('/user/login', data=data)

	def test_login(self):
		response = self.login(self.user_id, self.password)
		assert response.data == 'success'
		response = self.login(self.user_id, '123')
		assert response.data == 'wrong_password'
		response = self.login('wrong_user_id', '123456')
		assert response.data == 'wrong_user_id'

	def get_user_info(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getUserInfo', data=data)

	def test_get_user_info(self):
		response = self.get_user_info(self.user_id)
		user = json.loads(response.data)
		assert user['user_id'] == self.user_id and user['mobile'] == self.user_id and user['gender'] == 2

		response = self.get_user_info('wrong_user_id')
		assert response.data == 'failed'

	def set_user_info(self, **userinfo):
		return self.app.post('/user/setUserInfo', data=userinfo)

	def test_set_user_info(self):

		response = self.set_user_info(user_id='wrong_user_id', username='hehe')
		assert response.data == 'failed'

		response = self.set_user_info(user_id=self.user_id, username='hehe',
			mobile=self.user_id, university=u'大连理工大学',
			school=u'软件学院')
		assert response.data == 'success'

		response = self.get_user_info(self.user_id)
		data = json.loads(response.data)
		assert data['user_id'] == self.user_id and data['username'] == 'hehe'\
				and data['mobile'] == self.user_id and data['university'] == \
				u'大连理工大学' and data['school'] == u'软件学院'

	def is_university_known(self, user_id):
		data = dict(user_id = user_id)
		return self.app.post('/user/isUniversityKonwn', data = data)

	def test_is_university_known(self):
		response = self.is_university_known(self.user_id)
		assert response.data == 'true'

		response = self.is_university_known('18840824301')
		assert response.data == 'false'

		response = self.is_university_known('wrong_user_id')
		assert response.data == 'unregistered'

	def get_user_message(self, user_id):
		data = dict(user_id=user_id)
		return self.app.post('/user/getMessages', data=data)

	def test_get_messages(self):
		# calling method wish wrong user_id will return no 'failed' but empty
		# list of messages
		response = self.get_user_message(self.user_id)
		data = json.loads(response.data)
		assert len(data['messages']) == 0

		response = self.get_user_message('18763823371')
		data = json.loads(response.data)
		messages = data['messages']
		assert len(messages) != 0
		for message in messages:
			assert message['user_id'] == '18763823371'

	def clear_messages_by_user(self, user_id):
		data = dict(user_id = user_id)
		return self.app.post('/user/clearMessages', data = data)

	def test_clear_messages(self):
		response = self.clear_messages_by_user('15242605375')
		assert response.data == 'success'

		response = self.get_user_message('15242605375')
		data = json.loads(response.data)
		messages = data['messages']
		assert len(messages) == 0

	def feedback(self, user_id, content):
		data = dict(user_id = user_id, content = content)
		return self.app.post('/user/feedback', data = data)

	def test_feedback(self):
		content = u'用户反馈'
		response = self.feedback(self.user_id, content)
		assert 'success' == response.data

if __name__ == '__main__':
	unittest.main()