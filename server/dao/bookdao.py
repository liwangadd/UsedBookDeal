#!/usr/bin/env python
# coding: utf-8

'''define data access class for book collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime

import uuid

class BookDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self, configfile):
		super(BookDao, self).__init__(configfile)
		self.book = self.db.book
		self.user = self.db.user

	def insert_book(self, files, **book_info):
		time = strftime('%F %H:%m', localtime())
		imgs = []
		for f in files:
			img_id = str(uuid.uuid1())
			self.insert_img(img_id, f, book_info[Book.BOOK_ID],
				book_info[Book.BOOKNAME])
			imgs.append(img_id)
		book_info[Book.ADDED_TIME] = time
		book_info[Book.IMGS] = imgs
		book_info[Book.CLICKS] = 0
		book_info[Book.STATUS] = 0
		# insert book
		self.book.insert(book_info)
		# insert book_in into user's books
		result = self.user.update({User.USER_ID: book_info[Book.USER_ID]},
			{'$push': {User.BOOKS: book_info[Book.BOOK_ID] }})
		return result['updatedExisting']

	def get_book_info(self, book_id):
		# book's clicks increased by one
		result = self.book.update({Book.BOOK_ID: book_id}, \
			{'$inc': {Book.CLICKS: 1}})
		if not result['updatedExisting']:
			return None
		return self.book.find_one({Book.BOOK_ID: book_id})

	def set_book_info(self, book_id, **book_info):
		result = self.book.update({Book.BOOK_ID: book_id}, \
			{'$set': book_info})
		return result['updatedExisting']

	def set_book_status(self, book_id, status):
		result = self.book.update({Book.BOOK_ID: book_id}, \
			{'$set':{Book.STATUS: status} })
		return result['updatedExisting']

	def get_book_by_user(self, user_id):
		return self.book.find({Book.USER_ID: user_id})

 	def get_book_by_type(self, type, order_by, page, pagesize):
		pipeline = [{'$group': {'_id': '$'+Book.BOOKNAME, count:{'$sum':1} } }]
		cursor = self.book.aggregate(pipeline)
		for unit in cursor:
			unit[Book.IMGS] = self.get_imgs_by_bookname(bookname=unit. \
				get('_id'), limit=1)
		return cursor

	def get_book_by_name(self, bookname):
		return self.book.find({Book.BOOKNAME: bookname})

	def get_similar_name(self, bookname, limit):
		return self.book.find({Book.BOOKNAME: '/'+bookname+'/'}). \
			distinct(Book.BOOKNAME).limit(limit)

	def search_book(self, keyword, page, pagesize):
		pass