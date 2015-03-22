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
	def __init__(self):
		super(CommentDao, self).__init__()
		self.comment = self.db.comment

	def get_comments_by_object(self, object_id, page = None, pagesize = None):
		comments = self.comment.find({Comment.OBJECT_ID: object_id})

		if page is not None and pagesize is not None:
			skip = (page - 1) * pagesize
			comments = comments.skip(skip).limit(pagesize)

		return self.join_user_info(comments)

		# result = []
		# for comment in comments:
		# 	user_id = comment[Comment.USER_ID]
		# 	user = self.user.find_one({User.USER_ID: user_id})
		# 	comment[User.USERNAME] = user.get(User.USERNAME)
		# 	comment[User.GENDER] = user.get(User.GENDER)
		# 	result.append(comment)

		# return result

	def insert_comment(self, **comment_info):
		time = strftime('%F %T', localtime())
		comment_info[Comment.TIME] = time
		self.comment.insert(comment_info)
		return True

	def delete_comment(self, comment_id):
		self.comment.remove({Comment.COMMENT_ID: comment_id})
		self.comment.remove({Comment.TYPE: 1, Comment.ORIGINAL_COMMENT_ID: comment_id})


commentdao = CommentDao()