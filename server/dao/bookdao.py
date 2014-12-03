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
		self.collection = self.db.book

	def insert_book(self, files, **kw):
		time = strftime('%F %H:%m', localtime())
		imgs = []
		for f in files:
			img_id = uuid.uuid1()
			self.insert_img(img_id, f, book_id)
			imgs.append(img_id)
		self.collection.insert({Book.BOOK_ID: book_id, Book.BOOKNAME:bookname,\
			Book.USER_ID: user_id, Book.USERNAME: username, Book.TYPE: type, \
			Book.IMGS: imgs, Book.NEWNESS: newness, Book.AUDIENCE: audience, \
			Book.DESCRIPTION: description, Book.MOBILE: mobile, Book.QQ: qq, \
			Book.WEIXIN: weixin, Book.ADDED_TIME: time, Book.PRICE: price, \
			Book.STATUS: 0, Book.CLICKS: 0})
		return True

	def get_book_info(self, book_id):
		# book's clicks increased by one
		result = self.collection.update({Book.BOOK_ID: book_id}, \
			{'$inc': {Book.CLICKS: 1}})
		if not result['updatedExisting']:
			return None
		return self.collection.find_one({Book.BOOK_ID: book_id})

	def set_book_info(self, book_id, **book_info):
		result = self.collection.update({Book.BOOK_ID: book_id}, \
			{'$set': book_info})
		return result['updatedExisting']

	def set_book_status(self, book_id, status):
		result = self.collection.update({Book.BOOK_ID: book_id}, \
			{'$set':{Book.STATUS: status} })
		return result['updatedExisting']

	def get_book_by_user(self, user_id):
		return self.collection.find({User.USER_ID: user_id})

 	def get_book_by_type(self, type, order_by, page, pagesize):
		pipeline = [{'$group': {'_id': '$'+Book.BOOKNAME, count:{'$sum':1} } }]
		cursor = self.collection.aggregate(pipeline)
		for unit in cursor:
			unit[Book.IMGS] = self.get_imgs_by_bookname(bookname=unit. \
				get('_id'), limit=1)
		return cursor

	def get_book_by_name(self, bookname):
		return self.collection.find({Book.BOOKNAME: bookname})

	def get_similar_name(self, bookname, limit):
		return self.collection.find({Book.BOOKNAME: '/'+bookname+'/'}). \
			distinct(Book.BOOKNAME).limit(limit)

	def search_book(self, keyword, page, pagesize):
		pass