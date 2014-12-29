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
		self.wish = self.db.wish
		self.book = self.db.book

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

	def list_wishes(self, page, pagesize, sort = Wish.ADDED_TIME):
		skip = (page - 1) * pagesize
		return self.wish.find().sort([(sort, -1)]).skip(skip).\
				limit(pagesize)

	def list_books(self, type, sort, page, pagesize):
		skip = (page - 1) * pagesize
		if sort == Book.BOOKNAME:
			return self.book.find({Book.TYPE: type}).sort([(sort, 1)]).skip(skip).limit(pagesize)
		else:
			return self.book.find({Book.TYPE: type}).sort([(sort, -1)]).skip(skip).limit(pagesize)

admindao = AdminDao()