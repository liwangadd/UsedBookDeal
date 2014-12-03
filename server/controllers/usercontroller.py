#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of user module '''

from flask import *
from flask.blueprints import Blueprint
from dao.userdao import UserDao
from dao.fields import User
from utils.jsonutil import dbobject2dict

user_blueprint = Blueprint('user', __name__)
userdao = UserDao('dao_setting.cfg')

@user_blueprint.route('login')
def login():
	user_id = request.values.get('user_id')
	password = request.values.get('password')
	if user_id == None or password == None:
		return 'failed'
	if userdao.check_login(user_id, password):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('register')
def register():
	user_id = request.values.get('user_id')
	password = request.values.get('password')
	if user_id == None or password == None:
		return 'failed'
	if userdao.insert_user(user_id, password):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('getUserInfo')
def get_user_info():
	user_id = request.values.get('user_id')
	if user_id == None:
		return
	info = userdao.get_user_info(user_id)
	result = dbobject2dict(info, User.USER_ID, User.USERNAME, User.PASSWORD, \
		User.GENDER, User.MOBILE, User.QQ, User.WEIXIN, User.RELEASED_BOOKS, \
		User.WISHES)
	return jsonify(result)

@user_blueprint.route('setUserInfo')
def set_user_info():
	user_id = request.values.get('user_id')
	if user_id == None:
		return 'failed'
	username = request.values.get(User.USERNAME)
	password = request.values.get('password')
	gender = request.values.get('gender')
	mobile = request.values.get('mobile')
	qq = request.values.get('qq')
	weixin = request.values.get('weixin')

	try:
		gender = int(gender)
	except:
		gender = 2

	user_info = {}
	user_info[User.USERNAME] = username
	user_info[User.PASSWORD] = password
	user_info[User.GENDER] = gender
	user_info[User.MOBILE] = mobile
	user_info[User.QQ] = qq
	user_info[User.WEIXIN] = weixin
	if userdao.set_user_info(user_id, user_info):
		return 'success'
	else:
		return 'failed'

@user_blueprint.route('setUserImg')
def set_user_img():
	img = request.files.get('img')
	user_id = request.files.form.get('user_id')
	if img == None or user_id == None:
		return 'failed'
	if userdao.set_user_img(user_id, img):
		return 'success'
	else:
		return 'failed'