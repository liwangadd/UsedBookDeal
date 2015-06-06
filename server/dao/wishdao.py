#!/usr/bin/env python
# coding: utf-8

'''define data access class for wish collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
import uuid, pymongo

class WishDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self):
		super(WishDao, self).__init__()
		self.wish = self.db.wish
		self.user = self.db.user

	def list_wishes(self, status, type, order_by, page, pagesize):
		sort = [(order_by, -1)]
		skip = (page - 1) * pagesize
		# type == 0 means get all types of wish
		selection = {Wish.STATUS: status}
		if type is not None and type != 0:
			selection[Wish.TYPE] = type

		wishes = self.wish.find(selection, sort=sort, skip=skip,
				limit=pagesize)

		return self.join_user_info(wishes)

	def list_wishes_v1_5(self, university, order_by, school, page, pagesize):
		criteria = {}
		if university != '' and university != u'全部校区':
			criteria[User.UNIVERSITY] = university
		if order_by == User.GENDER:
			criteria[User.GENDER] = 0
		elif order_by == User.SCHOOL:
			criteria[User.SCHOOL] = school

		user_ids = self.user.distinct(User.USER_ID, criteria)

		skip = (page - 1) * pagesize

		if order_by == Wish.PRICE:
			wishes = self.wish.find( \
					{	Wish.USER_ID: {'$in': user_ids},
						Wish.STATUS: 0,
						Wish.REWARD: '0'},
					sort = [(Wish.PRICE, pymongo.DESCENDING)],
					skip = skip, limit = pagesize)
		else:
			wishes = self.wish.find( \
					{Wish.USER_ID: {'$in': user_ids}, Wish.STATUS: 0},
					skip = skip, limit = pagesize)

		return self.join_user_info(wishes)

	def get_wish_info(self, wish_id):
		wish = self.wish.find_one({Wish.WISH_ID: wish_id})
		if wish is None:
			return None
		user_id = wish[Wish.USER_ID]
		# find the referenced user and get its username and gender
		user = self.user.find_one({User.USER_ID: user_id})
		wish[User.USERNAME] = user.get(User.USERNAME)
		wish[User.GENDER] = user.get(User.GENDER)
		wish = self.delete__id(wish)
		return wish

	def insert_wish(self, files, **wish_info):

		imgs = []
		if files != None:
			for f in files:
				img_id = str(uuid.uuid1())
				self.insert_img(img_id, f, wish_info[Wish.WISH_ID],
					wish_info.get(Wish.BOOKNAME))
				imgs.append(img_id)
		wish_info[Wish.IMGS] = imgs

		time = strftime('%F %T', localtime())
		wish_info[Wish.ADDED_TIME] = time

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
		wishes =  self.wish.find({Wish.USER_ID: user_id}, sort=[(Wish.ADDED_TIME, pymongo.DESCENDING)])
		return self.cursor_to_list(wishes)

	def wish_clicks_plus(self, wish_id):
		# wish's clicks increased by one
		result = self.wish.update({Wish.WISH_ID: wish_id}, \
			{'$inc': {Wish.CLICKS: 1}})
		return result['updatedExisting']

wishdao = WishDao()