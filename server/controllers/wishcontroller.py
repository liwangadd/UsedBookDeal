#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of wish module '''

from flask import *
from flask.blueprints import Blueprint
from dao.wishdao import WishDao
from dao.fields import Wish
from utils.jsonutil import *
import uuid, base64

wish_blueprint = Blueprint('wish', __name__)
wishdao = WishDao('dao_setting.cfg')

@wish_blueprint.route('listWishes', methods=['GET', 'POST'])
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
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.USERNAME,
		Wish.IMGS, Wish.DESCRIPTION, Wish.ADDED_TIME, Wish.STATUS)
	return jsonify(wishes = wishes)

@wish_blueprint.route('getWsihInfo', methods=['GET', 'POST'])
def get_wish_info():
	wish_id = request.values.get(Wish.WISH_ID)
	if wish_id == None:
		return None
	wish = wishdao.get_wish_info(wish_id)
	wish = dbobject2dict(wish, Wish.WISH_ID, Wish.BOOKNAME, Wish.IMGS,
		Wish.USER_ID, Wish.USERNAME, Wish.DESCRIPTION, Wish.ADDED_TIME,
		Wish.MOBILE, Wish.QQ, Wish.WEIXIN)
	return jsonify(wish)

@wish_blueprint.route('makeWish', methods=['POST'])
def make_wish():
	try:
		user_id = request.form[Wish.USER_ID]
		username = request.form[Wish.USERNAME]
		bookname = request.form[Wish.BOOKNAME]
		description = request.form[Wish.DESCRIPTION]
	except:
		return 'failed'
	mobile = request.form.get(Wish.MOBILE)
	qq = request.form.get(Wish.QQ)
	weixin = request.form.get(Wish.WEIXIN)
	imgs = []
	for i in range(0, 5):
		try:
			img = request.form['img' + str(i)]
			img = img.encode('utf-8')
			img = base64.decodestring(img)
			imgs.append(img)
		except:
			break
	wish_id = str(uuid.uuid1())
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

@wish_blueprint.route('getWishesByUser', methods=['GET', 'POST'])
def get_wishes_by_user():
	user_id = request.values.get(Wish.USER_ID)
	if user_id == None:
		return None
	wishes = wishdao.get_wishes_by_user(user_id)
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.USERNAME,
		Wish.IMGS, Wish.DESCRIPTION, Wish.ADDED_TIME, Wish.STATUS)
	return jsonify(wishes=wishes)

@wish_blueprint.route('setWishInfo', methods=['GET', 'POST'])
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

@wish_blueprint.route('setWishStatus', methods=['GET', 'POST'])
def set_wish_status():
	try:
		wish_id = request.values[Wish.WISH_ID]
		user_id = request.values[Wish.USER_ID]
		status = request.values[Wish.STATUS]
	except:
		return 'failed'
	try:
		status = int(status)
	except:
		return 'failed'
	if wishdao.set_wish_status(wish_id, status) and \
		wishdao.insert_wish_token_message(str(uuid.uuid1()), user_id, wish_id):
		return 'success'
	else:
		return 'failed'
