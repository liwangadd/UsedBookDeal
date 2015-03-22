#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of comment module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.commentdao import commentdao
from ..dao.fields import *
from ..utils.jsonutil import *
import uuid

comment_blueprint = Blueprint('comment', __name__)

@comment_blueprint.route('makeComments', methods=['GET', 'POST'])
def make_comment():
	try:
		object_id = request.values[Comment.OBJECT_ID]
		user_id = request.values[Comment.USER_ID]
		username = request.values[Comment.USERNAME]
		content = request.values[Comment.CONTENT]
		assert object_id != '' and user_id != ''
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	try:
		comment_type = int(request.values[Comment.TYPE])
		assert comment_type == 0 or comment_type == 1
	except:
		comment_type = 0

	original_comment_id = request.values.get(Comment.ORIGINAL_COMMENT_ID)

	# add comment
	comment_id = str(uuid.uuid1())
	comment_info = {}
	comment_info[Comment.COMMENT_ID] = comment_id
	comment_info[Comment.OBJECT_ID] = object_id
	comment_info[Comment.USER_ID] = user_id
	comment_info[Comment.USERNAME] = username
	comment_info[Comment.CONTENT] = content
	comment_info[Comment.TYPE] = comment_type
	if original_comment_id != None:
		  comment_info[Comment.ORIGINAL_COMMENT_ID] = original_comment_id
	commentdao.insert_comment(**comment_info)
	# add message
	message_id = str(uuid.uuid1())
	commentdao.insert_comment_message(message_id, user_id, username,  content, object_id)
	return jsonify(comment_id = comment_id)

@comment_blueprint.route('getComments', methods=['GET', 'POST'])
def get_comments():
	''' return comments for a book/wish. if receive page and pagesize, return
	the specific page of comments, else return all the comments '''
	try:
		object_id = request.values[Comment.OBJECT_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'

	# page and pagesize can be None or int value
	try:
		page = request.values['page']
		pagesize = request.values['pagesize']
	except KeyError:
		page = None
		pagesize = None
	else:
		try:
			page = int(page)
			pagesize = int(pagesize)
		except:
			current_app.logger.error('invalid page or pagesize: %s, %s' % \
				(page, pagesize))
			return 'failed'

	comments = commentdao.get_comments_by_object(object_id, page, pagesize)
	# fields = Comment.ALL
	# fields.append(User.USERNAME)
	# fields.append(User.GENDER)
	# comments = cursor2list(comments, *fields)
	return jsonify(comments=comments)

@comment_blueprint.route('deleteComment', methods=['GET', 'POST'])
def delete_comment():
	try:
		comment_id = request.values[Comment.COMMENT_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'

	commentdao.delete_comment(comment_id)
	return 'success'