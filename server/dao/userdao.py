#!/usr/bin/env python
# coding: utf-8

'''define data access class for user collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
import uuid

class UserDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self):
		super(UserDao, self).__init__()

	def check_login(self, user_id, password):
		result = self.user.find_one({User.USER_ID: user_id})
		if result is not None:
			if result[User.PASSWORD] == password:
				return 'success'
			else:
				return 'wrong_password'
		else:
			return 'wrong_user_id'

	def insert_user(self, user_id, password):
		# set mobile as user_id and user's name as '淘书者' by default
		result = self.user.find_one({User.USER_ID: user_id})
		if result == None:
			self.user.insert({User.USER_ID: user_id, User.PASSWORD:
				password, User.USERNAME: u'淘书者', User.MOBILE: user_id,
				User.BOOKS: [],	User.WISHES: [], User.GENDER: 2})
			return True
		else:
			return False

	def get_user_info(self, user_id):
		result = self.user.find_one({User.USER_ID: user_id})
		return self.delete__id(result)

	def is_university_known(self, user_id):
		user = self.user.find_one({User.USER_ID: user_id})
		if user is None:
			return 'unregistered'

		university = user.get(User.UNIVERSITY)
		school = user.get(User.SCHOOL)
		if university is not None and school is not None:
			return 'true'
		else:
			return 'false'

	def set_user_info(self, user_id, **kw):
		if kw == {}:
			return True
		result = self.user.update({User.USER_ID: user_id}, \
			{'$set': kw})
		return result['updatedExisting']

	def set_user_img(self, user_id, file):
		user = self.user.find_one({User.USER_ID: user_id})
		if user == None:
			return False
		else:
			img_id = user.get(User.IMG)
			if img_id == None:
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, file, user_id)
			else:
				self.delete_img(img_id)
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, file, user_id)
			result = self.user.update({User.USER_ID: user_id},
				{'$set': {User.IMG: img_id}})
			return result['updatedExisting']

	def insert_feedback(self, user_id, content):
		user = self.user.find_one({User.USER_ID: user_id})
		if user == None:
			return False
		username = user[User.USERNAME]
		time = strftime('%F %T', localtime())
		self.feedback.insert({Feedback.USER_ID: user_id, Feedback.TIME: time,\
			Feedback.USERNAME: username, Feedback.CONTENT: content})
		return True

userdao = UserDao()