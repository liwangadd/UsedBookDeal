#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of user module '''

from flask import *
from flask.blueprints import Blueprint
from dao.userdao import userdao
from dao.fields import User, Message
from utils.jsonutil import dbobject2dict
import base64

user_blueprint = Blueprint('user', __name__)
# userdao = UserDao('dao_setting.cfg')

@user_blueprint.route('login', methods=['GET', 'POST'])
def login():
	try:
		user_id = request.values[User.USER_ID]
		password = request.values[User.PASSWORD]
	except:
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
	except:
		return 'failed'
	if userdao.insert_user(user_id, password):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('getUserInfo', methods=['GET', 'POST'])
def get_user_info():
	try:
		user_id = request.values[User.USER_ID]
	except:
		return jsonify({})
	info = userdao.get_user_info(user_id)
	if info == None:
		return jsonify({})
	result = dbobject2dict(info, User.USER_ID, User.USERNAME, User.PASSWORD,
		User.GENDER, User.MOBILE, User.QQ, User.WEIXIN, User.BOOKS,User.WISHES)
	return jsonify(result)

@user_blueprint.route('setUserInfo', methods=['GET', 'POST'])
def set_user_info():
	try:
		user_id = request.values[User.USER_ID]
	except:
		return 'failed'
	user_info = {}
	for keyword in (User.USERNAME, User.PASSWORD, User.GENDER, User.MOBILE,
			User.QQ, User.WEIXIN):
		try:
			value = request.values[keyword]
			if keyword == User.GENDER:
				try:
					value = int(value)
				except:
					return 'failed'
			user_info[keyword] = value
		except:
			pass
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
	except:
		return 'failed'
	img = img.encode('utf-8')
	img = base64.decodestring(img)
	if userdao.set_user_img(user_id, img):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('getMessages', methods=['POST'])
def get_messages_by_user():
	try:
		user_id = request.values[User.USER_ID]
	except:
		return 'failed'
	messages = userdao.get_messages_by_user(user_id)
	messages = cursor2list(messages, Message.MESSAGE_ID, Message.USER_ID,
		Message.TYPE, Message.CONTENT, Message.ANOTHER_USER_ID,
		Message.OBJECT_ID, Message.TIME, Message.IMG, Message.STATUS)
	return jsonify(messages=messages)