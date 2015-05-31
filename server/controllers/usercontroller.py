#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of user module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.userdao import userdao
from ..dao.fields import User, Message
from ..utils.jsonutil import *
import base64

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('getUniversitiesAndSchools', methods = ['GET', 'POST'])
def get_universities_and_schools():
	try:
		university = request.values['university']
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'

	data = userdao.get_universities_and_schools(university)
	return jsonify(data = data)

@user_blueprint.route('login', methods=['GET', 'POST'])
def login():
	try:
		user_id = request.values[User.USER_ID]
		password = request.values[User.PASSWORD]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	result = userdao.check_login(user_id, password)
	return result

@user_blueprint.route('register', methods=['GET', 'POST'])
def register():
	try:
		user_id = request.values[User.USER_ID]
		password = request.values[User.PASSWORD]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	if userdao.insert_user(user_id, password):
		return 'success'
	else:
		return 'conflict_user_id'

@user_blueprint.route('getUserInfo', methods=['GET', 'POST'])
def get_user_info():
	try:
		user_id = request.values[User.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	info = userdao.get_user_info(user_id)
	try:
		assert info is not None
	except AssertionError:
		current_app.logger.error('invalid user_id: %s' % user_id)
		return 'failed'
	# result = dbobject2dict(info, *User.ALL)
	return jsonify(info)

@user_blueprint.route('setUserInfo', methods=['GET', 'POST'])
def set_user_info():
	try:
		user_id = request.values[User.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	user_info = {}
	for keyword in User.ALL:
		try:
			value = request.values[keyword]
		except KeyError:
			pass
		else:
			if keyword == User.USER_ID:
				continue
			elif keyword == User.GENDER:
				try:
					value = int(value)
					assert value >= 0 and value <= 2
				except:
					current_app.logger.error('invalid gender: %s' % value)
					return 'failed'
			elif keyword == User.PASSWORD and value == '':
				continue
			user_info[keyword] = value

	if userdao.set_user_info(user_id, **user_info):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('isUniversityKnown', methods = ['POST', 'GET'])
def is_university_known():
	try:
		user_id = request.values[User.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'

	result = userdao.is_university_known(user_id)
	return result

@user_blueprint.route('setPassword', methods=['POST', 'GET'])
def set_user_password():
	try:
		user_id = request.values[User.USER_ID]
		password = request.values[User.PASSWORD]
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	user_info = {}
	user_info[User.PASSWORD] = password
	if userdao.set_user_info(user_id, **user_info):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('setImg', methods=['POST'])
def set_user_img():
	try:
		user_id = request.form[User.USER_ID]
		# img = request.files['img']
		img = request.form['img']
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	img = img.encode('utf-8')
	img = base64.decodestring(img)
	if userdao.set_user_img(user_id, img):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('getMessages', methods=['POST', 'GET'])
def get_messages_by_user():
	try:
		user_id = request.values[User.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	messages = userdao.get_messages_by_user(user_id)
	# messages = cursor2list(messages, *Message.ALL)
	userdao.set_messages_read(user_id)
	return jsonify(messages=messages)

@user_blueprint.route('clearMessages', methods = ['POST', 'GET'])
def clear_messages_by_user():
	""" the type of messages will be set 2, instead of really deleting all
	messages"""
	try:
		user_id = request.values[User.USER_ID]
		assert user_id != ''
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	if userdao.delete_messages(user_id):
		return 'success'
	else:
		current_app.logger.error('no messages found for user: %s' % user_id)
		return 'failed'

@user_blueprint.route('feedback', methods = ['POST', 'GET'])
def feedback():
	try:
		user_id = request.values[User.USER_ID]
		content = request.values['content']
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	if userdao.insert_feedback(user_id, content):
		return 'success'
	return 'failed'