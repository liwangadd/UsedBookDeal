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
import setting

class BaseDao(object):
	'''@arg configfile: file name of config file '''
	def __init__(self, configfile):
		super(BaseDao, self).__init__()
		# config_parser = ConfigParser()
		# f = open(configfile)
		# try:
		# 	config_parser.readfp(f)
		# 	host = config_parser.get('mongo', 'host')
		# 	port = config_parser.getint('mongo', 'port')
		# 	database = config_parser.get('mongo', 'database')
		# except:
		# 	raise
		# finally:
		# 	f.close()
		self.mongo = MongoClient(setting.HOST, setting.PORT)
		self.db = self.mongo[setting.DATABASE]
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
			return self.fs.get(f_id)

	def get_user_img(self, user_id):
		img = self.image.find_one({Image.OBJECT_ID: user_id})
		if img == None:
			return None
		else:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			return self.fs.get(f_id)

	def get_imgs_by_bookname(self, bookname, limit):
		pass

	def insert_comment_message(self, message_id, user_id, object_id):
		message = {}
		message[Message.MESSAGE_ID] = message_id
		message[Message.OBJECT_ID] = object_id
		message[Message.ANOTHER_USER_ID] = user_id
		book = self.book.find_one({Book.BOOK_ID: object_id})
		if book != None:
			message[Message.TYPE] = Message.BOOK_COMMENTED
			message[Message.USER_ID] = book[Book.USER_ID]
			message[Message.IMG] = book[Book.IMGS][0]
			message[Message.CONTENT] = book[Book.BOOKNAME]
			self.message.insert(message)
			return True
		wish = self.wish.find_one({Wish.WISH_ID: object_id})
		if wish != None:
			message[Message.TYPE] = Message.WISH_COMMENTED
			message[Message.USER_ID] = wish[Wish.USER_ID]
			message[Message.CONTENT] = wish[Wish.BOOKNAME]
			# if there if no image for this wish, the user' head image
			# will be set as message's image
			wish_imgs = wish.get(Wish.IMGS)
			if wish_imgs != None and wish_imgs != []:
				message[Message.IMG] = wish_imgs[0]
			else:
				user = self.user.find_one({User.USER_ID: wish[Wish.USER_ID]})
				if user == None:
					return False
				message[Message.IMG] = user.get(User.IMG)
			self.message.insert(message)
			return True
		return False

	def insert_wish_token_message(self, message_id, user_id, object_id):
		message = {}
		message[Message.MESSAGE_ID] = message_id
		message[Message.OBJECT_ID] = object_id
		message[Message.ANOTHER_USER_ID] = user_id
		message[Message.TYPE] = Message.WISH_TOKEN
		wish = self.wish.find_one({Wish.WISH_ID: object_id})
		if wish != None:
			message[Message.USER_ID] = wish[Wish.USER_ID]
			message[Message.CONTENT] = wish[Wish.BOOKNAME]
			# if there if no image for this wish, the user' head image
			# will be set as message's image
			wish_imgs = wish.get(Wish.IMGS)
			if wish_imgs != None and wish_imgs != []:
				message[Message.IMG] = wish_imgs[0]
			else:
				user = self.user.find_one({User.USER_ID: wish[Wish.USER_ID]})
				if user == None:
					return False
				message[Message.IMG] = user.get(User.IMG)
			self.message.insert(message)
			return True
		return False

	def insert_system_message(self, message_id, user_id, content):
		time = strftime('%F %H:%m', localtime())
		user = self.user.find_one({User.USER_ID: user_id})
		if user == None:
			return False
		message = {}
		message[Message.MESSAGE_ID] = message_id
		message[Message.USER_ID] = user_id
		message[Message.TYPE] = Message.SYSTEM_MESSAGE
		message[Message.CONTENT] = content
		message[Message.IMG] = user[User.IMG]
		message[Message.ANOTHER_USER_ID] = None
		message[Message.OBJECT_ID] = None
		self.message.insert(message)
		return True

	def get_message(self, message_id):
		return self.message.find_one({Message.MESSAGE_ID: message_id})

	def get_messages_by_user(self, user_id):
		return self.message.find({Message.USER_ID: user_id})