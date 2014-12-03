#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of comment module '''

from flask import *
from flask.blueprints import Blueprint
from dao.commentdao import CommentDao
from dao.fields import Comment
from utils.jsonutil import *
import uuid

comment_blueprint = Blueprint('comment', __name__)
commentdao = CommentDao('dao_setting.cfg')

@comment_blueprint.route('makeComment')
def make_comment():
	try:
		object_id = request.values[Comment.OBJECT_ID]
		user_id = request.values[Comment.USER_ID]
		username = request.values[Comment.USERNAME]
		content = request.values[Comment.CONTENT]
		floor = int(request.values[Comment.FLOOR])
	except:
		return 'failed'
	comment_id = uuid.uuid1()
	comment_info = {}
	comment_info[Comment.COMMEND_ID] = comment_id
	comment_info[Comment.OBJECT_ID] = object_id
	comment_info[Comment.USER_ID] = user_id
	comment_info[Comment.USERNAME] = username
	comment_info[Comment.CONTENT] = content
	comment_info[Comment.FLOOR] = floor
	commentdao.insert_comment(**comment_info)
	return 'success'

@comment_blueprint.route('getComments')
def get_comments():
	try:
		object_id = request.values[Comment.OBJECT_ID]
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		return None
	comments = commentdao.get_comments_by_object(object_id, page, pagesize)
	if comments == None:
		return None
	comments = dbobject2dict(comments, Comment.COMMEND_ID, Comment.USER_ID, \
		Comment.USERNAME, Comment.TIME, Comment.FLOOR, Comment.CONTENT)
	return jsonify(comments=comments)