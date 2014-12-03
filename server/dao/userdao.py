#!/usr/bin/env python
# coding: utf-8

'''define data access class for user collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
import uuid

class UserDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self, configfile):
		super(UserDao, self).__init__(configfile)
		self.collection = self.db.user

	def check_login(self, user_id, password):
		result = self.collection.find({User.USER_ID: user_id, User.PASSWORD: \
			password})
		if result:
			return True
		else:
			return False

	def insert_user(self, user_id, password):
		result = self.collection.find_one({User.USER_ID: user_id})
		if result == None:
			self.collection.insert({User.USER_ID: user_id, User.PASSWORD:\
				password})
			return True
		else:
			return False

	def get_user_info(self, user_id):
		result = self.collection.find_one({User.USER_ID: user_id})
		return result

	def set_user_info(self, user_id, **kw):
		result = self.collection.update({User.USER_ID: user_id}, \
			{'$set': kw})
		return result['updatedExisting']

	def set_user_img(self, user_id, file):
		user = self.collection.find_one({User.USER_ID: user_id})
		if user == None:
			return False
		else:
			img_id = user.get(User.IMG)
			if img_id == None:
				img_id = uuid.uuid1()
				self.insert_img(img_id, file, object_id=user_id)
			else:
				self.set_img(img_id, file)
			return True
