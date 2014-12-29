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

@user_blueprint.route('login', methods=['GET', 'POST'])
def login():
	try:
		user_id = request.values[User.USER_ID]
		password = request.values[User.PASSWORD]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	if userdao.check_login(user_id, password):
		return 'success'
	else:
		return 'failed'

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
		return 'failed'

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
	result = dbobject2dict(info, *User.ALL)
	return jsonify(result)

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
	messages = cursor2list(messages, *Message.ALL)
	return jsonify(messages=messages)