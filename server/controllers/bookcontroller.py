#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of book module '''

from flask import *
from flask.blueprints import Blueprint
from dao.bookdao import BookDao
from dao.fields import Book
from utils.jsonutil import *
import uuid

book_blueprint = Blueprint('book', __name__)
bookdao = BookDao('dao_setting.cfg')

@book_blueprint.route('releaseBook')
def release_book():
	user_id = request.values.get(Book.USER_ID)
	username = request.values.get(Book.USERNAME)
	bookname = request.values.get(Book.BOOKNAME)
	price = request.values.get(Book.PRICE)
	booktype = request.values.get(Book.TYPE)
	newness = request.values.get(Book.NEWNESS)
	audience = request.values.get(Book.AUDIENCE)
	description = request.values.get(Book.DESCRIPTION)
	mobile = request.values.get(Book.MOBILE)
	qq = request.values.get(Book.QQ)
	weixin = request.values.get(Book.WEIXIN)
	if user_id == None or bookname == None or booktype == None or price ==None\
		or (mobile == None and qq == None and weixin == None):
		return 'failed'
	try:
		price = float(price)
		booktype = int(booktype)
	except:
		return 'failed'

	imgs = []
	for key, f in request.files:
		imgs.append(f)
	book_id = uuid.uuid1()
	book_info = {}
	book_info[Book.BOOK_ID] = book_id
	book_info[Book.USER_ID] = user_id
	book_info[Book.USERNAME] = username
	book_info[Book.BOOKNAME] = bookname
	book_info[Book.PRICE] = price
	book_info[Book.TYPE] = booktype
	book_info[Book.NEWNESS] = newness
	book_info[Book.AUDIENCE] audience
	book_info[Book.DESCRIPTION] = description
	book_info[Book.MOBILE] = mobile
	book_info[Book.QQ] = qq
	book_info[Book.WEIXIN] = weixin
	bookdao.insert_book(imgs, **book_info)
	return 'success'

@book_blueprint.route('setBookInfo')
def set_book_info():
	user_id = request.values.get(Book.USER_ID)
	book_id = request.values.get(Book.BOOK_ID)
	bookname = request.values.get(Book.BOOKNAME)
	booktype = request.values.get(Book.TYPE)
	price = request.values.get(Book.PRICE)
	newness = request.values.get(Book.NEWNESS)
	audience = request.values.get(Book.AUDIENCE)
	description = request.values.get(Book.DESCRIPTION)
	mobile = request.values.get(Book.MOBILE)
	qq = request.values.get(Book.QQ)
	weixin = request.values.get(Book.WEIXIN)
	if user_id == None or book_id == None:
		return 'failed'
	try:
		price = float(price)
		booktype = int(booktype)
	except:
		return 'failed'
	book_info[Book.BOOKNAME] = bookname
	book_info[Book.PRICE] = price
	book_info[Book.TYPE] = booktype
	book_info[Book.NEWNESS] = newness
	book_info[Book.AUDIENCE] audience
	book_info[Book.DESCRIPTION] = description
	book_info[Book.MOBILE] = mobile
	book_info[Book.QQ] = qq
	book_info[Book.WEIXIN] = weixin
	if bookdao.set_book_info(book_id, book_info):
		return 'success'
	else:
		return 'failed'

@book_blueprint.route('getBookInfo')
def get_book_info():
	book_id = request.values.get(Book.BOOK_ID)
	if book_id == None:
		return None
	book = bookdao.get_book_info(book_id)
	if book == None:
		return None
	book = dbobject2dict(book,Book.BOOK_ID,Book.BOOKNAME,Book.TYPE,Book.PRICE,\
		Book.USER_ID, Book.USERNAME, Book.IMGS, Book.NEWNESS, Book.AUDIENCE, \
		Book.DESCRIPTION, Book.ADDED_TIME, Book.STATUS, Book.MOBILE, Book.QQ, \
		Book.WEIXIN)
	return jsonify(book)

@book_blueprint.route('setBookStatus')
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

@book_blueprint.route('getBookByUser')
def get_book_by_user():
	user_id = request.values.get(Book.USER_ID)
	if user_id == None:
		return 'failed'
	books = bookdao.get_book_by_user(user_id)
	if books == None:
		return 'failed'
	books = cursor2list(books, Book.BOOK_ID, Book.BOOKNAME, Book.TYPE, \
		Book.IMGS, Book.ADDED_TIME, Book.STATUS)
	return jsonify(books=books)

@book_blueprint.route('getBookByType')
def get_book_by_type():
	booktype = request.values.get(Book.TYPE)
	order_by = request.values.get('order_by')
	page = request.values.get('page')
	pagesize = request.values.get('pagesize')
	if booktype == None:
		return None
	if order_by == None:
		order_by = Book.ADDED_TIME
	try:
		page = int(page)
		pagesize = int(pagesize)
	except:
		return None
	books = bookdao.get_book_by_type(booktype, order_by, page, pagesize)
	books = cursor2list(books, Book.BOOKNAME, Book.IMGS, 'count')
	return jsonify(books=books)

@book_blueprint.route('getBookByName')
def get_book_by_name():
	# return the first book's info and other books' id
	bookname = request.values.get(Book.BOOKNAME)
	if bookname == None:
		return None
	books = bookdao.get_book_by_name(bookname)
	if books == None or books.count() == 0:
		return None
	# get the first book's info
	result = {}
	for key, value in books[0]:
		if key != '_id':
			result[key] = values
	# get other books' id
	other_book_ids = []
	for book in books[1:]:
		other_book_ids.append(book[Book.BOOK_ID])
	result['other_book_ids'] = other_book_ids
	return jsonify(result)

@book_blueprint.route('getSimilarBookname')
def get_similar_name():
	bookname = request.values.get(Book.BOOKNAME)
	limit = request.values.get('limit')
	if bookname == None:
		return None
	names = bookdao.get_similar_name(bookname, limit)
	booknames = []
	for name in names:
		booknames.append(name[Book.BOOKNAME])
	return jsonify(booknames=booknames)

@book_blueprint.route('searchBook')
def search_book():
	keyword = request.values.get('keyword')
	if keyword == None:
		return None
