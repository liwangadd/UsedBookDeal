#!/usr/bin/env python
# coding: utf-8

'''define data access class for admin collection'''

from basedao import BaseDao
from fields import *

class AdminDao(BaseDao):
	def __init__(self):
		super(AdminDao, self).__init__()
		self.admin = self.db.admin
		self.user = self.db.user

	def check_login(self, admin_id, password):
		if self.admin.find({Admin.ADMIN_ID: admin_id,
			Admin.PASSWORD: password}):
			return True
		else:
			return False

	def set_info(self, admin_id, **info):
		result = self.admin.update({Admin.ADMIN_ID: admin_id},
			{'$set': info})
		return result['updatedExisting']

	def list_users(self, page, pagesize):
		skip = (page - 1) * pagesize
		return self.user.find({}).skip(skip).limit(pagesize)

admindao = AdminDao()