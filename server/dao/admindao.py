#!/usr/bin/env python
# coding: utf-8

'''define data access class for admin collection'''

from basedao import BaseDao
from fields import *
import pymongo

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

	def set_password(self, admin_id, password):
		result = self.admin.update({Admin.ADMIN_ID: admin_id},
			{'$set': info})
		return result['updatedExisting']

	def count_user(self):
		return self.user.count()

	def list_users(self, page, pagesize):
		skip = (page - 1) * pagesize
		users = self.user.find({}).skip(skip).limit(pagesize)
		return self.cursor_to_list(users)

	def count_wish(self):
		return self.wish.count()

	def list_wishes(self, page, pagesize, sort = Wish.ADDED_TIME):
		skip = (page - 1) * pagesize
		wishes = self.wish.find().sort([(sort, -1)]).skip(skip).\
				limit(pagesize)
		return self.cursor_to_list(wishes)

	def count_book(self):
		return self.book.count()

	def list_books(self, type, sort, page, pagesize):
		skip = (page - 1) * pagesize
		if sort == Book.BOOKNAME:
			books = self.book.find({Book.TYPE: type}).sort([(sort, pymongo.ASCENDING)]).skip(skip).limit(pagesize)
		else:
			books = self.book.find({Book.TYPE: type}).sort([(sort, pymongo.DESCENDING)]).skip(skip).limit(pagesize)

		return self.cursor_to_list(books)

admindao = AdminDao()