#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of book module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.bookdao import bookdao
from ..dao.fields import Book, User
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
		assert user_id != ''
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	book_info = {}
	book_info[Book.USER_ID] = user_id
	for key in Book.ALL:
		try:
			value = request.values[key]
		except KeyError:
			pass
		else:
			if key == Book.BOOK_ID:
				continue
			elif key == Book.TYPE:
				try:
					value = int(value)
					assert value > 0 and value <= 6
				except:
					current_app.logger.error('invalid type: %s' % value)
					return 'failed'
			elif key == Book.TYPE_V1_5:
				try:
					value = int(value)
					assert value > 0 and value <= 8
				except:
					current_app.logger.error('invalid type_v1_5: %s' % value)
					return 'failed'
			elif key == Book.STATUS:
				try:
					value = int(value)
					assert value == 0 or value == 1
				except:
					current_app.logger.error('invalid status: %s' % value)
					return 'failed'
			elif key == Book.PRICE:
				try:
					value = float(value)
				except:
					current_app.logger.error('invalid price: %s' % value)
					return 'failed'
			book_info[key] = value

	imgs = []
	for i in range(1, 4):
		try:
			img = request.values['img' + str(i)]
			assert img != ''
		except:
			continue
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
			current_app.logger.error('error in insert_book, book_info: %s' % book_info)
			return 'failed'
	else:
		# modify book information
		if bookdao.set_book_info(book_id, imgs, **book_info):
			return 'success'
		else:
			current_app.logger.error('error in set_book_info, book_info: %s' % book_info)
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

	return jsonify(book)

@book_blueprint.route('setBookStatus', methods=['GET', 'POST'])
def set_book_status():
	try:
		book_id = request.values[Book.BOOK_ID]
		status = int(request.values[Book.STATUS])
		assert status == 0 or status == 1 or status == 2
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

	# order_by is set added_time by default
	try:
		order_by = request.values['order_by']
	except KeyError:
		order_by = Book.ADDED_TIME
	if order_by != Book.ADDED_TIME and order_by != Book.CLICKS:
		current_app.logger.error('invalid arg(order_by: %s)' % order_by)
		return 'failed'

	books = bookdao.get_book_by_type(booktype, order_by, page, pagesize)

	# return whether there is new messages if user has logged in
	user_id = request.values.get(User.USER_ID)
	has_messages = False
	if user_id != None and user_id != '':
		has_messages = bookdao.has_new_messages(user_id)

	return jsonify(books=books, has_messages=has_messages)

@book_blueprint.route('getBooksByTypeV1_5', methods = ['GET', 'POST'])
def get_book_by_type_v1_5():
	try:
		type_v1_5 = int(request.values[Book.TYPE_V1_5])
		university = request.values[User.UNIVERSITY]
		assert type_v1_5 >= 0 and type_v1_5 <= 8
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	try:
		audience_v1_5 = request.values[Book.AUDIENCE_V1_5]
	except KeyError:
		audience_v1_5 = None

	# order_by is set added_time by default
	try:
		order_by = request.values['order_by']
	except KeyError:
		order_by = Book.ADDED_TIME
	if order_by != Book.ADDED_TIME and order_by != Book.CLICKS and \
			order_by != User.GENDER and order_by != Book.PRICE and \
			order_by!= Book.SCORE:
		current_app.logger.error('invalid arg(order_by: %s)' % order_by)
		return 'failed'

	books = bookdao.get_book_by_type_v1_5(type_v1_5, university, order_by, audience_v1_5, page, pagesize)
	return jsonify(books = books)

@book_blueprint.route('HomePage', methods = ['GET', 'POST'])
def home_page():
	try:
		university = request.values[User.UNIVERSITY]
	except:
		current_app.logger.error('invalid arg')
		return 'failed'

	books = bookdao.get_book_by_type_v1_5(0, university, Book.ADDED_TIME,
			None, 1, 2)
	books2 = bookdao.get_book_by_type_v1_5(0, university, Book.CLICKS, None,
			1, 2)
	books.extend(books2)
	return jsonify(books = books)

@book_blueprint.route('getBestReviews', methods = ['GET', 'POST'])
def get_best_reviews():
	try:
		university = request.values[User.UNIVERSITY]
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	books = bookdao.get_best_reviews(university, page, pagesize)
	return jsonify(books = books)

@book_blueprint.route('getRecommendedBooks', methods = ['GET', 'POST'])
def get_recommended_books():
	try:
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	books = bookdao.get_recommended_books(page, pagesize)

	return jsonify(books = books)

@book_blueprint.route('getBooksByName', methods=['GET', 'POST'])
def get_book_by_name():
	try:
		bookname = request.values[Book.BOOKNAME]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	books = bookdao.get_book_by_name(bookname)
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

	# booktype can be None or an int value
	try:
		booktype = request.values[Book.TYPE]
	except KeyError:
		booktype = None
	else:
		try:
			booktype = int(booktype)
		except:
			current_app.logger.error('invalid booktype: %s' % booktype)
			return 'failed'

	keywords = keyword.split(' ')
	ok, books = bookdao.search_book(keywords, page, pagesize, booktype)
	if ok:
		return jsonify(books=books)
	else:
		current_app.logger.error('DocNotFoundError, keywords: %s' % keywords)
		return jsonify(books = [])

@book_blueprint.route('bookClicked', methods=['GET', 'POST'])
def book_clicked():
	''' book's clisk increased by one (book's clicks is a int variable used to
		present the popularity of a book)  '''
	try:
		book_id = request.values[Book.BOOK_ID]
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	if bookdao.book_clicks_plus(book_id):
		return 'success'
	else:
		return 'failed'