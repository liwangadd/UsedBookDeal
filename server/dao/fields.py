#!/usr/bin/env python
# coding: utf-8

''' define strings that define the names of collections' fields in database'''

class User(object):
	"""field names of user collection"""
	USER_ID = 'user_id'
	USERNAME = 'username'
	PASSWORD = 'password'
	GENDER = 'gender'  # 1: male, 0: female
	UNIVERSITY = 'university'
	SCHOOL = 'school'
	IMG = 'img'
	MOBILE = 'mobile'
	QQ = 'qq'
	WEIXIN = 'weixin'
	BOOKS = 'books'
	WISHES = 'wishes'
	ALL = [USER_ID, USERNAME, PASSWORD, GENDER, UNIVERSITY, SCHOOL, IMG,
		MOBILE, QQ, WEIXIN, BOOKS, WISHES]

class Book(object):
	"""field names of book collection"""
	BOOK_ID = 'book_id'
	USER_ID = 'user_id'
	USERNAME = 'username'
	ADDED_TIME = 'added_time'
	BOOKNAME = 'bookname'
	IMGS = 'imgs'
	PRICE = 'price'
	TYPE = 'type'
	NEWNESS = 'newness'
	AUDIENCE = 'audience'
	DESCRIPTION = 'description'
	CLICKS = 'clicks'
	MOBILE = 'mobile'
	QQ = 'qq'
	WEIXIN = 'weixin'
	STATUS = 'status'  # 0: default, not saled , 1: saled, 2: removed
	ALL = [BOOK_ID, USER_ID, USERNAME, ADDED_TIME, BOOKNAME, IMGS, PRICE, TYPE,
		NEWNESS, AUDIENCE, DESCRIPTION, CLICKS, MOBILE, QQ, WEIXIN, STATUS]

class Wish(object):
	"""field name of wish collection"""
	WISH_ID = 'wish_id'
	BOOKNAME = 'bookname'
	USER_ID = 'user_id'
	USERNAME = 'username'
	TYPE = 'type'
	IMGS = 'imgs'
	DESCRIPTION = 'description'
	MOBILE = 'mobile'
	QQ = 'qq'
	WEIXIN = 'weixin'
	ADDED_TIME = 'added_time'
	CLICKS = 'clicks'
	STATUS = 'status'  # 0: default, not achieved, 1: achieved, 2: someone want to help achieve it but it's not done yet
	ALL = [WISH_ID, BOOKNAME, USER_ID, USERNAME, TYPE, IMGS, DESCRIPTION, MOBILE, QQ, WEIXIN, ADDED_TIME, CLICKS, STATUS]

class Image(object):
	"""field names of image collection"""
	IMG_ID = 'img_id'
	OBJECT_ID = 'object_id'
	BOOKNAME = 'bookname'
	CATEGORY = 'category'  # 0: inserted by default, 1: inserted by user
	FILE_ID = 'file_id'
	# FILENAME = 'filename'
	ALL = [IMG_ID, OBJECT_ID, BOOKNAME, CATEGORY, FILE_ID]

class Comment(object):
	"""field names of comment collection"""
	COMMENT_ID = 'comment_id'
	OBJECT_ID = 'object_id'
	USER_ID = 'user_id'
	USERNAME = 'username'
	TIME = 'time'
	FLOOR = 'floor'
	CONTENT = 'content'
	TYPE = 'type' # 0: general comment, 1: reply
	ORIGINAL_COMMENT_ID = 'original_comment_id' # the comment which this one is replying to
	ALL = [COMMENT_ID, OBJECT_ID, USER_ID, USERNAME, TIME, FLOOR, CONTENT,
			TYPE, ORIGINAL_COMMENT_ID]

class Message(object):
	"""field names of message collection"""
	MESSAGE_ID = 'message_id'
	USER_ID = 'user_id'
	TYPE = 'type' # 0: system message, 1: user's book is commented, 2: user's wish is commented, 3: others can achieve user's wish
	CONTENT = 'content'
	ANOTHER_USER_ID = 'another_user_id'
	USERNAME = 'username' # another user's name
	OBJECT_ID = 'object_id'
	BOOKNAME = 'bookname'
	TIME = 'time'
	IMG = 'img'
	STATUS = 'status' # 0: unread, 1: read, 2: "deleted" by user
	ALL = [MESSAGE_ID, USER_ID, TYPE, CONTENT, ANOTHER_USER_ID, USERNAME,
		OBJECT_ID, BOOKNAME, TIME, IMG, STATUS]

	# message types
	SYSTEM_MESSAGE = 0
	BOOK_COMMENTED = 1
	WISH_COMMENTED = 2
	WISH_TOKEN = 3

class Admin(object):
	"""field names of admin collection"""
	ADMIN_ID = 'admin_id'
	PASSWORD = 'password'