#!/usr/bin/env python
# coding: utf-8

''' define base data access class which provide file access methods and is
used for inherited by other data access class '''

from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from ConfigParser import ConfigParser
from time import localtime, strftime
from fields import *
from gridfs.errors import *
from .. import setting
import pymongo

class BaseDao(object):
	''':param configfile: file name of config file '''
	def __init__(self):
		super(BaseDao, self).__init__()
		self.mongo = MongoClient(setting.HOST, setting.PORT)
		self.db = self.mongo[setting.DATABASE]
		self.user = self.db.user
		self.image = self.db.image
		self.message = self.db.message
		self.book = self.db.book
		self.wish = self.db.wish
		self.fs = GridFS(self.db, collection='img_files')

	# def set_img(self, img_id, f):
	# 	img = self.image.find_one({Image.IMG_ID: img_id})
	# 	if img == None:
	# 		return False
	# 	else:
	# 		old_f_id = img.get(Image.FILE_ID)
	# 		new_f_id = self.fs.put(f)
	# 		new_f_id = unicode(new_f_id)
	# 		self.image.update({Image.IMG_ID: img_id}, {'$set': {Image.FILE_ID:
	# 			new_f_id}} )
	# 		self.fs.delete(ObjectId(old_f_id))
	# 		return True

	# def set_img_by_object(self, object_id, f):
	# 	img = self.image.find_one({Image.OBJECT_ID: object_id})
	# 	if img == None:
	# 		return False
	# 	else:
	# 		old_f_id = img.get(Image.FILE_ID)
	# 		new_f_id = self.fs.put(f)
	# 		new_f_id = unicode(new_f_id)
	# 		self.image.update({Image.OBJECT_ID:object_id},
	# 			{'$set': {Image.FILE_ID:new_f_id}} )
	# 		self.fs.delete(old_f_id)
	# 		return True

	def insert_img(self, img_id, f, object_id, bookname=None, category=1):
		# file_id = self.fs.put(f, filename=f.name)
		file_id = self.fs.put(f)
		file_id = unicode(file_id)
		if bookname == None:
			self.image.insert({Image.IMG_ID: img_id, Image.OBJECT_ID:
				object_id, Image.CATEGORY: category, Image.FILE_ID: file_id})
		else:
			self.image.insert({Image.IMG_ID: img_id, Image.OBJECT_ID:
				object_id, Image.BOOKNAME: bookname, Image.CATEGORY: category,
				Image.FILE_ID: file_id})
		return True

	def delete_img(self, img_id):
		# only images inserted by user can be deleted
		img = self.image.find_one({Image.IMG_ID: img_id, Image.CATEGORY: 1})
		if img != None:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			self.fs.delete(f_id)
			self.image.remove({Image.IMG_ID: img_id, Image.CATEGORY: 1})
		return True

	def delete_img_by_object(self, object_id):
		cursor = self.image.find({Image.OBJECT_ID:object_id, Image.CATEGORY:1})
		for img in cursor:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			self.fs.delete(f_id)
		self.image.remove({Image.OBJECT_ID:object_id, Image.CATEGORY:1})

	def get_img(self, img_id):
		img = self.image.find_one({Image.IMG_ID: img_id})
		if img == None:
			return None
		else:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			try:
				f =  self.fs.get(f_id)
			except NoFile:
				return None
			return f

	def get_user_img(self, user_id):
		img = self.image.find_one({Image.OBJECT_ID: user_id})
		if img == None:
			return None
		else:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			return self.fs.get(f_id)

	def get_imgs_by_bookname(self, bookname, limit):
		imgs = self.image.find(
			{Image.BOOKNAME: {'$regex': '.*?'+bookname+'.*?'}},
			sort=[(Image.CATEGORY, pymongo.ASCENDING)], limit=limit)
		return self.cursor_to_list(imgs)

	def insert_comment_message(self, message_id, user_id, username, content,
			object_id):
		message = {}
		message[Message.MESSAGE_ID] = message_id
		message[Message.OBJECT_ID] = object_id
		message[Message.ANOTHER_USER_ID] = user_id
		message[Message.USERNAME] = username
		message[Message.CONTENT] = content
		message[Message.STATUS] = 0
		time = strftime('%F %H:%m', localtime())
		message[Message.TIME] = time

		book = self.book.find_one({Book.BOOK_ID: object_id})
		# if the object_id is a id of a book
		if book != None:
			message[Message.TYPE] = Message.BOOK_COMMENTED
			message[Message.USER_ID] = book[Book.USER_ID]
			message[Message.BOOKNAME] = book[Book.BOOKNAME]
			book_imgs = book.get(Book.IMGS)
			if book_imgs != None and len(book_imgs) != 0:
				message[Message.IMG] = book_imgs[0]
			else:
				user = self.user.find_one({User.USER_ID: book[Book.USER_ID]})
				if user == None:
					return False
				message[Message.IMG] = user.get(User.IMG)
			self.message.insert(message)
			return True

		wish = self.wish.find_one({Wish.WISH_ID: object_id})
		# if the object_id is a id of a wish
		if wish != None:
			message[Message.TYPE] = Message.WISH_COMMENTED
			message[Message.USER_ID] = wish[Wish.USER_ID]
			message[Message.BOOKNAME] = wish[Wish.BOOKNAME]
			# if there if no image for this wish, the user' head image
			# will be set as message's image
			wish_imgs = wish.get(Wish.IMGS)
			if wish_imgs != None and len(wish_imgs) != 0:
				message[Message.IMG] = wish_imgs[0]
			else:
				user = self.user.find_one({User.USER_ID: wish[Wish.USER_ID]})
				if user == None:
					return False
				message[Message.IMG] = user.get(User.IMG)
			self.message.insert(message)
			return True
		return False

	def insert_wish_token_message(self, message_id, user_id, username,
			object_id):
		message = {}
		message[Message.MESSAGE_ID] = message_id
		message[Message.OBJECT_ID] = object_id
		message[Message.ANOTHER_USER_ID] = user_id
		message[Message.USERNAME] = username
		message[Message.TYPE] = Message.WISH_TOKEN
		message[Message.STATUS] = 0
		time = strftime('%F %H:%m', localtime())
		message[Message.TIME] = time
		wish = self.wish.find_one({Wish.WISH_ID: object_id})
		if wish != None:
			message[Message.USER_ID] = wish[Wish.USER_ID]
			message[Message.BOOKNAME] = wish[Wish.BOOKNAME]
			# if there if no image for this wish, the user' head image
			# will be set as message's image
			wish_imgs = wish.get(Wish.IMGS)
			if wish_imgs != None and len(wish_imgs) != 0:
				message[Message.IMG] = wish_imgs[0]
			else:
				user = self.user.find_one({User.USER_ID: wish[Wish.USER_ID]})
				if user == None:
					return False
				message[Message.IMG] = user[User.IMG]
			self.message.insert(message)
			return True
		return False

	def insert_system_message(self, message_id, user_id, content):
		user = self.user.find_one({User.USER_ID: user_id})
		if user == None:
			return False
		message = {}
		time = strftime('%F %H:%m', localtime())
		message[Message.TIME] = time
		message[Message.MESSAGE_ID] = message_id
		message[Message.USER_ID] = user_id
		message[Message.TYPE] = Message.SYSTEM_MESSAGE
		message[Message.CONTENT] = content
		message[Message.IMG] = user[User.IMG]
		message[Message.STATUS] = 0
		self.message.insert(message)
		return True

	def get_message(self, message_id):
		message = self.message.find_one({Message.MESSAGE_ID: message_id})
		return self.delete__id(message)

	def has_new_messages(self, user_id):
		''' whether there is new messages for the user '''
		messages = self.message.find({Message.USER_ID: user_id,
			Message.STATUS: 0})
		return (messages.count() != 0)

	def get_messages_by_user(self, user_id):
		''' get unread messages of a user '''
		messages = self.message.find(
			{Message.USER_ID: user_id, Message.STATUS: {'$in': [0, 1]} },
			sort = [(Message.TIME, pymongo.DESCENDING)])
		return self.cursor_to_list(messages)

	def set_messages_read(self, user_id):
		result = self.message.update(
			{Message.USER_ID: user_id, Message.STATUS: 0},
			{'$set': {Message.STATUS: 1}}, multi = True)
		return result['updatedExisting']

	def delete_messages(self, user_id):
		""" the type of messages will be set 2, instead of really deleting all
		messages"""
		result = self.message.update({Message.USER_ID: user_id},
			{'$set': {Message.TYPE: 2}}, multi = True)
		return result['updatedExisting']

	def delete__id(self, db_object):
		try:
			db_object.pop('_id')
			return db_object
		except:
			return None

	def cursor_to_list(self, cursor):
		# transfer cursor to list
		result = []
		for db_object in cursor:
			db_object.pop('_id')
			result.append(db_object)
		return result

	def join_user_info(self, cursor):
		# transfer cursor to list and join user information
		result = []

		for db_object in cursor:
			db_object.pop('_id')
			user_id = db_object[User.USER_ID]
			user = self.user.find_one({User.USER_ID: user_id})
			db_object[User.USERNAME] = user[User.USERNAME]
			db_object[User.GENDER] = user[User.GENDER]
			result.append(db_object)

		return result

basedao = BaseDao()