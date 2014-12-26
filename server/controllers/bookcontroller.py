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

@book_blueprint.route('setBookInfo', methods=['GET', 'POST'])
def set_book_info():
	''' add new book or modify book information '''
	book_id = request.values.get(Book.BOOK_ID)
	try:
		user_id = request.values[Book.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
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
				current_app.logger.error('error in setBookInfo: invalid args:(type or price:%s)'%value)
				return 'failed'
			book_info[key] = value
		except KeyError:
			pass

	book_info[Book.USER_ID] = user_id
	imgs = []
	for i in range(1, 4):
		try:
			img = request.values['img' + str(i)]
		except KeyError:
			break
		img = img.encode('utf-8')
		img = base64.decodestring(img)
		imgs.append(img)
	if book_id == None or book_id == '':
		# add new book
		book_id = str(uuid.uuid1())
		book_info[Book.BOOK_ID] = book_id
		if bookdao.insert_book(imgs, **book_info):
			# set book removed after specific time setted in config file
			scheduler.add_set_book_removed_job(book_id)
			return 'success'
		else:
			return 'failed'
	else:
		# modify book information
		if bookdao.set_book_info(book_id, imgs, **book_info):
			return 'success'
		else:
			return 'failed'


@book_blueprint.route('getBookInfo', methods=['GET', 'POST'])
def get_book_info():
	try:
		book_id = request.values[Book.BOOK_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	book = bookdao.get_book_info(book_id)
	try:
		assert book is not None
	except AssertionError:
		current_app.logger.error('error in getBookInfo: invalid book_id: %s' % book_id)
		return 'failed'
	book = dbobject2dict(book,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(book)

@book_blueprint.route('setBookStatus', methods=['GET', 'POST'])
def set_book_status():
	try:
		book_id = request.values[Book.BOOK_ID]
		status = int(request.values[Book.STATUS])
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	if bookdao.set_book_status(book_id, status):
		return 'success'
	else:
		return 'failed'

@book_blueprint.route('getBooksByUser', methods=['GET', 'POST'])
def get_book_by_user():
	try:
		user_id = request.values[Book.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	books = bookdao.get_book_by_user(user_id)
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
		current_app.logger.error('invalid args')
		return 'failed'

	# order_by is defaulted as added time
	try:
		order_by = request.values['order_by']
	except KeyError:
		order_by = Book.ADDED_TIME
	if order_by != Book.ADDED_TIME and order_by != Book.CLICKS:
		current_app.logger.error('invalid arg(order_by: %s)' % order_by)
		return 'failed'
	books = []
	cursor = bookdao.get_book_by_type(booktype, order_by, page, pagesize)
	for dbobject in cursor:
		book = {}
		book[Book.BOOKNAME] = dbobject.get('_id')
		book['img'] = dbobject.get('img')
		book['count'] = dbobject.get('count')
		books.append(book)
	return jsonify(books=books)

@book_blueprint.route('getBooksByName', methods=['GET', 'POST'])
def get_book_by_name():
	try:
		bookname = request.values[Book.BOOKNAME]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	books = bookdao.get_book_by_name(bookname)
	books = cursor2list(books,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(books=books)

@book_blueprint.route('getSimilarBookname', methods=['GET', 'POST'])
def get_similar_name():
	try:
		bookname = request.values[Book.BOOKNAME]
		limit = int(request.values['limit'])
	except:
		current_app.logger.error('invalid args')
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
		current_app.logger.error('invalid args')
		return 'failed'
	booktype = request.values.get(Book.TYPE)
	keywords = keyword.split(' ')
	books = bookdao.search_book(keywords, page, pagesize)
	books = cursor2list(books,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(books=books)
