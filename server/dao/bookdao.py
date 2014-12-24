#!/usr/bin/env python
# coding: utf-8

'''define data access class for book collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
from ..utils.xapiansearch import xapian_tool
import uuid, re

class BookDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self):
		super(BookDao, self).__init__()
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

	def set_book_info(self, book_id, files, **book_info):
		if files != None and files != []:
			self.delete_img_by_object(book_id)
			imgs = []
			for f in files:
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, f, book_id,
					book_info.get(Book.BOOKNAME))
				imgs.append(img_id)
			book_info[Book.IMGS] = imgs
		result = self.book.update({Book.BOOK_ID: book_id}, {'$set': book_info})
		return result['updatedExisting']

	def set_book_status(self, book_id, status):
		result = self.book.update({Book.BOOK_ID: book_id}, \
			{'$set':{Book.STATUS: status} })
		# if status == 1:
		# 	xapian_tool.delete_document(book_id)
		return result['updatedExisting']

	def get_book_by_user(self, user_id):
		return self.book.find({Book.USER_ID: user_id})

	def get_book_by_type(self, booktype, order_by, page, pagesize):
		pipeline = [
				{'$match': {Book.TYPE: booktype}},
				{'$group': {'_id': '$'+Book.BOOKNAME,'count':{'$sum':1},
					order_by: {'$max': order_by}} },
				{'$sort': {Book.ADDED_TIME: -1} }]
		result = self.book.aggregate(pipeline)
		cursor = result['result']
		for unit in cursor:
			imgs = self.get_imgs_by_bookname(bookname=unit.get('_id'), limit=1)
			try:
				unit['img'] = imgs[0]
			except IndexError:
				unit['img'] = None
		return cursor

	def get_book_by_name(self, bookname):
		return self.book.find({Book.BOOKNAME: bookname})

	def get_similar_name(self, bookname, limit):
		return self.book.find(
			{Image.BOOKNAME: {'$regex': r'.*?'+bookname+'.*?'}},
			limit=limit).distinct(Book.BOOKNAME)

	def get_books_by_ids(self, book_ids, booktype):
		if booktype is None:
			return self.book.find({Book.BOOK_ID: {'$in': book_ids}})
		else:
			return self.book.find({Book.BOOK_ID: {'$in': book_ids},
				Book.TYPE: booktype})

	def search_book(self, keywords, page, pagesize, booktype=None):
		book_ids = xapian_tool.search(keywords, page, pagesize)
		return self.get_books_by_ids(book_ids, booktype)

bookdao = BookDao()