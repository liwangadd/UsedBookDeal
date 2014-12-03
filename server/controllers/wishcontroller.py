#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of wish module '''

from flask import *
from flask.blueprints import Blueprint
from dao.wishdao import WishDao
from dao.fields import Wish
from utils.jsonutil import *
import uuid

wish_blueprint = Blueprint('wish', __name__)
wishdao = WishDao('dao_setting.cfg')

@wish_blueprint.route('listWishes')
def list_wishes():
	order_by = request.values.get('order_by')
	if order_by != Wish.ADDED_TIME and order_by != Wish.CLICKS:
		return None
	status = request.values.get(Wish.STATUS)
	page = request.values.get('page')
	pagesize = request.values.get('pagesize')
	try:
		status = int(status)
		page = int(page)
		pagesize = int(pagesize)
	except:
		return None
	wishes = wishdao.list_wishes(status, order_by, page, pagesize)
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.USERNAME, \
		Wish.IMGS, Wish.DESCRIPTION, Wish.ADDED_TIME, Wish.STATUS)
	return jsonify(wishes = wishes)

@wish_blueprint.route('getWsihInfo')
def get_wish_info():
	wish_id = request.values.get(Wish.WISH_ID)
	if wish_id == None:
		return None
	wish = wishdao.get_wish_info(wish_id)
	wish = dbobject2dict(wish, Wish.WISH_ID, Wish.BOOKNAME, Wish.IMGS, \
		Wish.USER_ID, Wish.USERNAME, Wish.DESCRIPTION, Wish.ADDED_TIME, \
		Wish.MOBILE, Wish.QQ, Wish.WEIXIN)
	return jsonify(wish)

@wish_blueprint.route('makeWish')
def make_wish():
	user_id = request.form.get(Wish.USER_ID)
	username = request.form.get(Wish.USERNAME)
	bookname = request.form.get(Wish.BOOKNAME)
	description = request.form.get(Wish.DESCRIPTION)
	mobile = request.form.get(Wish.MOBILE)
	qq = request.form.get(Wish.QQ)
	weixin = request.form.get(Wish.WEIXIN)
	if user_id == None or bookname == None or description == None:
		return 'failed'
	imgs = []
	for key, f in request.files:
		imgs.append(f)
	wish_id = uuid.uuid1()
	wish_info = {}
	wish_info[Wish.WISH_ID] = wish_id
	wish_info[Wish.USER_ID] = user_id
	wish_info[Wish.USERNAME] = username
	wish_info[Wish.BOOKNAME] = bookname
	wish_info[Wish.DESCRIPTION] = description
	wish_info[Wish.MOBILE] = mobile
	wish_info[Wish.QQ] = qq
	wish_info[Wish.WEIXIN] = weixin
	wishdao.insert_wish(imgs, **wish_info)
	return 'success'

@wish_blueprint.route('getWishesByUser')
def get_wishes_by_user():
	user_id = request.values.get(Wish.USER_ID)
	if user_id == None:
		return None
	wishes = wishdao.get_wishes_by_user(user_id)
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.USERNAME, \
		Wish.IMGS, Wish.DESCRIPTION, Wish.ADDED_TIME, Wish.STATUS)
	return jsonify(wishes=wishes)

@wish_blueprint('setWishInfo')
def set_wish_info():
	wish_id = request.values.get(Wish.WISH_ID)
	user_id = request.values.get(Wish.USER_ID)
	bookname = request.values.get(Wish.BOOKNAME)
	description = request.values.get(Wish.DESCRIPTION)
	mobile = request.values.get(Wish.MOBILE)
	qq = request.values.get(Wish.QQ)
	weixin = request.values.get(Wish.WEIXIN)
	if wish_id == None or user_id == None:
		return 'failed'
	wish_info = {}
	wish_info[Wish.BOOKNAME] = bookname
	wish_info[Wish.DESCRIPTION] = description
	wish_info[Wish.MOBILE] = mobile
	wish_info[Wish.QQ] = qq
	wish_info[Wish.WEIXIN] = weixin
	if wishdao.set_wish_info(wish_id, wish_info):
		return 'success'
	else:
		return 'failed'

@wish_blueprint('setWishStatus')
def set_wish_status():
	wish_id = request.values.get(Wish.WISH_ID)
	user_id = request.values.get(Wish.USER_ID)
	if wish_id == None or user_id == None:
		return 'failed'
	status = request.values.get(Wish.STATUS)
	try:
		status = int(status)
	except:
		return 'failed'
	if wishdao.set_wish_status(wish_id, status):
		return 'success'
	else:
		return 'failed'
