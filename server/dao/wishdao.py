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
	def __init__(self, configfile):
		super(WishDao, self).__init__(configfile)
		self.collection = self.db.wish

	def list_wishes(self, status, order_by, page, pagesize):
		sort = [(order_by, -1)]
		skip = (page - 1) * pagesize
		return self.collection.find({Wish.STATUS: status}, sort=sort, \
			skip=skip, limit=limit)

	def get_wish_info(self, wish_id):
		return wish = self.collection.find_one({Wish.WISH_ID: wish_id})

	def insert_wish(self, files, **kw):
		imgs = []
		time = strftime('%F %H:%m', localtime())
		if files != None:
			for f in files:
				img_id = uuid.uuid1()
				self.insert_img(img_id, f, wish_id, bookname)
				imgs.append(img_id)
		kw[Wish.IMGS] = imgs
		kw[Wish.STATUS] = 0
		kw[Wish.CLICKS] = 0
		self.collection.insert(kw)
		return True

	def set_wish_info(self, wish_id, **kw):
		result = self.collection.update({Wish.WISH_ID: wish_id}, {'$set': kw})
		return result['updatedExisting']

	def set_wish_status(self, wish_id, status):
		result = self.collection.update({Wish.WISH_ID: wish_id}, {'$set': \
			{Wish.STATUS: status}})
		return result['updatedExisting']

	def get_wishes_by_user(self, user_id):
		return self.collection.find({Wish.USER_ID: user_id})