#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of book module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.bookdao import bookdao
from ..dao.fields import Book
from ..utils.jsonutil import *
from ..utils.scheduler import scheduler
import uuid, base64

book_blueprint = Blueprint('book', __name__)
# bookdao = BookDao('dao_setting.cfg')

# @book_blueprint.route('releaseBook', methods=['POST'])
# def release_book():
# 	try:
# 		user_id = request.values[Book.USER_ID]
# 		username = request.values[Book.USERNAME]
# 		bookname = request.values[Book.BOOKNAME]
# 		price = request.values[Book.PRICE]
# 		booktype = request.values[Book.TYPE]
# 	except:
# 		return 'failed'
# 	newness = request.values.get(Book.NEWNESS)
# 	audience = request.values.get(Book.AUDIENCE)
# 	description = request.values.get(Book.DESCRIPTION)
# 	mobile = request.values.get(Book.MOBILE)
# 	qq = request.values.get(Book.QQ)
# 	weixin = request.values.get(Book.WEIXIN)
# 	if mobile == None and qq == None and weixin == None:
# 		print 'mobile and qq and weixin are None'
# 		return 'failed'
# 	try:
# 		price = float(price)
# 		booktype = int(booktype)
# 	except:
# 		print 'price is not float or booktype is not int'
# 		return 'failed'
# 	imgs = []
# 	for i in range(1, 4):
# 		try:
# 			img = request.form['img' + str(i)]
# 		except:
# 			print i, 'img' + str(i)
# 			break
# 		img = img.encode('utf-8')
# 		img = base64.decodestring(img)
# 		imgs.append(img)

# 	book_id = str(uuid.uuid1())
# 	book_info = {}
# 	book_info[Book.BOOK_ID] = book_id
# 	book_info[Book.USER_ID] = user_id
# 	book_info[Book.USERNAME] = username
# 	book_info[Book.BOOKNAME] = bookname
# 	book_info[Book.PRICE] = price
# 	book_info[Book.TYPE] = booktype
# 	book_info[Book.NEWNESS] = newness
# 	book_info[Book.AUDIENCE] = audience
# 	book_info[Book.DESCRIPTION] = description
# 	book_info[Book.MOBILE] = mobile
# 	book_info[Book.QQ] = qq
# 	book_info[Book.WEIXIN] = weixin
# 	if bookdao.insert_book(imgs, **book_info):
# 		return 'success'
# 	else:
# 		return 'failed'

@book_blueprint.route('setBookInfo', methods=['GET', 'POST'])
def set_book_info():
	try:
		book_id = request.values[Book.BOOK_ID]
		user_id = request.values[Book.USER_ID]
	except:
		return 'failed'
	book_info = {}
	for key in (Book.USERNAME, Book.BOOKNAME, Book.TYPE, Book.PRICE,
			Book.NEWNESS, Book.AUDIENCE, Book.DESCRIPTION, Book.MOBILE,
			Book.QQ, Book.WEIXIN):
		try:
			value = request.values[key]
			try:
				if key == Book.TYPE:
					value = int(value)
				elif key == Book.PRICE:
					value = float(value)
			except:
				return 'failed'
			book_info[key] = value
		except:
			pass
	book_info[Book.USER_ID] = user_id
	imgs = []
	for i in range(1, 4):
		try:
			img = request.values['img' + str(i)]
		except:
			break
		img = img.encode('utf-8')
		img = base64.decodestring(img)
		imgs.append(img)
	print 'book_id', book_id
	if book_id == '':
		book_id = str(uuid.uuid1())
		book_info[Book.BOOK_ID] = book_id
		if bookdao.insert_book(imgs, **book_info):
			# set book removed after specific time setted in config file
			scheduler.add_set_book_removed_job(book_id)
			return 'success'
		else:
			return 'failed'
	else:
		if bookdao.set_book_info(book_id, imgs, **book_info):
			return 'success'
		else:
			return 'failed'


@book_blueprint.route('getBookInfo', methods=['GET', 'POST'])
def get_book_info():
	book_id = request.values.get(Book.BOOK_ID)
	if book_id == None:
		return 'failed'
	book = bookdao.get_book_info(book_id)
	if book == None:
		return 'failed'
	book = dbobject2dict(book,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(book)

@book_blueprint.route('setBookStatus', methods=['GET', 'POST'])
def set_book_status():
	book_id = request.values.get(Book.BOOK_ID)
	status = request.values.get(Book.STATUS)
	if book_id == None:
		return 'failed'
	try:
		status = int(status)
	except:
		return 'failed'
	if bookdao.set_book_status(book_id, status):
		return 'success'
	else:
		return 'failed'

@book_blueprint.route('getBooksByUser', methods=['GET', 'POST'])
def get_book_by_user():
	user_id = request.values.get(Book.USER_ID)
	if user_id == None:
		return 'failed'
	books = bookdao.get_book_by_user(user_id)
	if books == None:
		return 'failed'
	books = cursor2list(books,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(books=books)

@book_blueprint.route('getBooksByType', methods=['GET', 'POST'])
def get_book_by_type():
	try:
		booktype = int(request.values[Book.TYPE])
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		return 'failed'
	# order_by is defaulted as added time
	order_by = request.values.get('order_by')
	if order_by == None:
		order_by = Book.ADDED_TIME
	if order_by != Book.ADDED_TIME and order_by != Book.CLICKS:
		return 'failed'
	books = []
	cursor = bookdao.get_book_by_type(booktype, order_by, page, pagesize)
	for dbobject in cursor:
		book = {}
		book[Book.BOOKNAME] = dbobject.get('_id')
		book['img'] = dbobject.get('img')
		book['count'] = dbobject.get('count')
		books.append(book)
	# books = cursor2list(books, Book.BOOKNAME, Book.IMGS, 'count')
	return jsonify(books=books)

@book_blueprint.route('getBooksByName', methods=['GET', 'POST'])
def get_book_by_name():
	# return the first book's info and other books' id
	bookname = request.values.get(Book.BOOKNAME)
	if bookname == None:
		return 'failed'
	books = bookdao.get_book_by_name(bookname)
	books = cursor2list(books,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	# # get the first book's info
	# result = {}
	# for key, value in books[0]:
	# 	if key != '_id':
	# 		result[key] = values
	# # get other books' id
	# other_book_ids = []
	# for book in books[1:]:
	# 	other_book_ids.append(book[Book.BOOK_ID])
	# result['other_book_ids'] = other_book_ids
	return jsonify(books=books)

@book_blueprint.route('getSimilarBookname', methods=['GET', 'POST'])
def get_similar_name():
	try:
		bookname = request.values[Book.BOOKNAME]
		limit = int(request.values['limit'])
	except:
		return 'failed'
	names = bookdao.get_similar_name(bookname, limit)
	return jsonify(booknames=names)

@book_blueprint.route('searchBook', methods=['GET', 'POST'])
def search_book():
	try:
		keyword = request.values['keyword']
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		return 'failed'
	booktype = request.values.get(Book.TYPE)
	keywords = keyword.split(' ')
	books = bookdao.search_book(keywords, page, pagesize)
	books = cursor2list(books,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(books=books)
