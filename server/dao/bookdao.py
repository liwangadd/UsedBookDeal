#!/usr/bin/env python
# coding: utf-8

'''define data access class for book collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
from ..utils.xapiansearch import xapian_tool
import uuid, re, pymongo

class BookDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self):
		super(BookDao, self).__init__()
		self.book = self.db.book
		self.user = self.db.user

	def insert_book(self, files, **book_info):

		imgs = []
		for f in files:
			img_id = str(uuid.uuid1())
			self.insert_img(img_id, f, book_info[Book.BOOK_ID],
				book_info[Book.BOOKNAME])
			imgs.append(img_id)
		book_info[Book.IMGS] = imgs

		time = strftime('%F %T', localtime())
		book_info[Book.ADDED_TIME] = time

		book_info[Book.CLICKS] = 0
		book_info[Book.STATUS] = 0

		# insert book
		self.book.insert(book_info)

		# insert book_in into user's books
		result = self.user.update({User.USER_ID: book_info[Book.USER_ID]},
			{'$push': {User.BOOKS: book_info[Book.BOOK_ID] }})

		return result['updatedExisting']

	def get_book_info(self, book_id):
		book = self.book.find_one({Book.BOOK_ID: book_id})
		if book is None:
			return None
		return self.join_user_info(book)

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
		return result['updatedExisting']

	def get_book_by_user(self, user_id):
		books = self.book.find({Book.USER_ID: user_id}, sort=[(Book.ADDED_TIME, pymongo.DESCENDING)])
		return self.cursor_to_list(books)

	def get_book_by_type(self, booktype, order_by, page, pagesize):
		skip = (page - 1) * pagesize
		pipeline = [
				{'$match': {Book.TYPE: booktype, Book.STATUS: 0}},
				{'$group':
					{
					'_id': '$'+Book.BOOKNAME,
					'count':{'$sum': 1},
					order_by: {'$max': '$'+order_by},
					Book.PRICE: {'$min': '$'+Book.PRICE}
					}
				},
				{'$sort': {order_by: -1} },
				{'$skip': skip },
				{'$limit': pagesize}
		]

		cursor = self.book.aggregate(pipeline)
		result = []
		for unit in cursor:
			unit[Book.BOOKNAME] = unit['_id']
			unit.pop('_id')

			book = self.book.find_one({Book.BOOKNAME: unit[Book.BOOKNAME]},
					sort = [(Book.PRICE, pymongo.ASCENDING)])
			try:
				unit['img'] = book[Book.IMGS][0]
			except:
				unit['img'] = None
			result.append(unit)
		return result

	def get_book_by_type_v1_5(self, type_v1_5, university, order_by, audience,
			page, pagesize):
		if order_by != User.GENDER:
			user_ids = self.user.distinct(User.USER_ID, {User.UNIVERSITY: university})
		else:
			user_ids = self.user.distinct(User.USER_ID, {User.UNIVERSITY: university, User.GENDER: 0})

		criteria = {Book.USER_ID: {'$in': user_ids}}
		if type_v1_5 != 0:
			criteria[Book.TYPE_V1_5] = type_v1_5

		if audience != None and audience != 'null':
			criteria[Book.AUDIENCE] = audience

		skip = (page - 1) * pagesize

		if order_by == User.GENDER:
			books = self.book.find(criteria, skip = skip, limit = pagesize,
				sort = [(Book.ADDED_TIME, pymongo.DESCENDING)])
		elif order_by == Book.PRICE:
			books = self.book.find(criteria, skip = skip, limit = pagesize,
				sort = [(Book.PRICE, pymongo.ASCENDING)])
		else:
			books = self.book.find(criteria, skip = skip, limit = pagesize, sort = [(order_by, pymongo.DESCENDING)])
		return self.join_user_info(books)

	def get_recommended_books(self, page, pagesize):
		skip = (page - 1) * pagesize
		books = self.book.find({}, skip = skip, limit = pagesize)
		return self.join_user_info(books)

	def get_book_by_name(self, bookname):
		books = self.book.find({Book.BOOKNAME: bookname, Book.STATUS: 0},
				sort=[(Book.PRICE, pymongo.ASCENDING)])
		return self.join_user_info(books)

	def get_similar_name(self, bookname, limit):
		books = self.book.find(
			{Image.BOOKNAME: {'$regex': r'.*?'+bookname+'.*?'}},
			limit=limit).distinct(Book.BOOKNAME)
		return books

	def get_books_by_ids(self, book_ids, booktype):

		selection = {Book.BOOK_ID: {'$in': book_ids}}
		if booktype is not None and booktype != 0 and booktype != '':
			selection[Book.TYPE] = booktype

		books = self.book.find(selection)
		return self.join_user_info(books)

		# if booktype is None or booktype == 0 or booktype == '':
		# 	return self.book.find({Book.BOOK_ID: {'$in': book_ids}})
		# else:
		# 	booktype = int(booktype)
		# 	return self.book.find({Book.BOOK_ID: {'$in': book_ids},
		# 		Book.TYPE: booktype})

	def search_book(self, keywords, page, pagesize, booktype=None):
		book_ids = xapian_tool.search(keywords, page, pagesize)
		return self.get_books_by_ids(book_ids, booktype)

	def book_clicks_plus(self, book_id):
		# book's clicks increased by one
		result = self.book.update({Book.BOOK_ID: book_id}, \
			{'$inc': {Book.CLICKS: 1}})
		return result['updatedExisting']

bookdao = BookDao()