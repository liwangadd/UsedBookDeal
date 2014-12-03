#!/usr/bin/env python
# coding: utf-8

'''define data access class for comment collection'''

from basedao import BaseDao
from fields import *
from pymongo import MongoClient
from time import localtime, strftime
import uuid

class CommentDao(BaseDao):
	''' @args configfile: filename of config file'''
	def __init__(self, configfile):
		super(CommentDao, self).__init__(configfile)
		self.collection = self.db.comment

	def get_comments_by_object(self, object_id, page, pagesize):
		skip = (page - 1) * pagesize
		return self.collection.find({Comment.OBJECT_ID: object_id}) \
			.skip(skip).limit(pagesize)

	def insert_comment(self, **comment_info):
		self.collection.insert({Comment.OBJECT_ID: object_id, Comment.USER_ID:\
			user_id, Comment.USERNAME: username, Comment.CONTENT: content})
		return True