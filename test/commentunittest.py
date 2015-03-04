# coding: utf-8

import unittest, json, sys
reload(sys)
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/')
sys.setdefaultencoding('utf-8')

from server.myapp import app

class CommentTestCase(unittest.TestCase):
	"""unit test case for web interfaces"""

	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		self.object_id = 'b14ca33e-833e-11e4-afcb-642737f58199'
		self.user_id = '18742513130'

	def make_comment(self, object_id, user_id, username, content):
		data = dict(object_id = object_id, user_id = user_id, \
				username = username, content = content)
		return self.app.post('/comment/makeComments', data = data)

	def test_make_comment(self):
		username = u'呵呵'
		content = u'个人消息测试'
		response = self.make_comment(self.object_id, self.user_id, username, content)
		assert response.data == 'success'

	def get_comments(self, object_id):
		data = dict(object_id = object_id)
		return self.app.post('/comment/getComments', data = data)

	def test_get_comments(self):
		response = self.get_comments(self.object_id)
		data = json.loads(response.data)
		comments = data['comments']
		for comment in comments:
			assert comment['object_id'] == self.object_id

		response = self.get_comments('wrong_object_id')
		data = json.loads(response.data)
		comments = data['comments']
		assert len(comments) == 0

if __name__ == '__main__':
	unittest.main()