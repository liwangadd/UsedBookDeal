#!/usr/bin/env python
# coding: utf-8

'''define data access class for wish collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
import uuid

class WishDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self):
		super(WishDao, self).__init__()
		self.wish = self.db.wish
		self.user = self.db.user

	def list_wishes(self, status, order_by, page, pagesize):
		sort = [(order_by, -1)]
		skip = (page - 1) * pagesize
		return self.wish.find({Wish.STATUS: status}, sort=sort, \
			skip=skip, limit=pagesize)

	def get_wish_info(self, wish_id):
		return self.wish.find_one({Wish.WISH_ID: wish_id})

	def insert_wish(self, files, **wish_info):
		imgs = []
		time = strftime('%F %H:%m', localtime())
		if files != None:
			for f in files:
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, f, wish_info[Wish.WISH_ID],
					wish_info.get(Wish.BOOKNAME))
				imgs.append(img_id)
		wish_info[Wish.IMGS] = imgs
		wish_info[Wish.STATUS] = 0
		wish_info[Wish.CLICKS] = 0
		# insert wish
		self.wish.insert(wish_info)
		# insert wish_id into user's wishes
		result = self.user.update({User.USER_ID: wish_info[Wish.USER_ID]},
			{'$push': {User.WISHES: wish_info[Wish.WISH_ID]} })
		return result['updatedExisting']

	def set_wish_info(self, files, wish_id, **wish_info):
		if files != None and files != []:
			self.delete_img_by_object(wish_id)
			imgs = []
			for f in files:
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, f, wish_id,
					wish_info.get(Wish.BOOKNAME))
				imgs.append(img_id)
			wish_info[Wish.IMGS] = imgs
		result = self.wish.update({Wish.WISH_ID: wish_id}, {'$set': wish_info})
		return result['updatedExisting']

	def set_wish_status(self, wish_id, status):
		result = self.wish.update({Wish.WISH_ID: wish_id}, {'$set': \
			{Wish.STATUS: status}})
		return result['updatedExisting']

	def reset_wish_status(self, wish_id):
		''' check wish's status 24 hours after user's wish was token by
		others, if the status is not set 1 which means the wishes was
		achieved, set the status 0(not achieved) '''
		result = self.wish.find_one({Wish.WISH_ID: wish_id})
		if result == None:
			return False
		status = result.get(Wish.STATUS)
		if status != 1:
			result = self.wish.update({Wish.WISH_ID: wish_id}, {'$set': \
				{Wish.STATUS: 0}})
		return True

	def get_wishes_by_user(self, user_id):
		return self.wish.find({Wish.USER_ID: user_id})

wishdao = WishDao()