#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of wish module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.wishdao import wishdao
from ..dao.fields import Wish
from ..utils.jsonutil import *
from ..utils.scheduler import scheduler
import uuid, base64

wish_blueprint = Blueprint('wish', __name__)

@wish_blueprint.route('listWishes', methods=['GET', 'POST'])
def list_wishes():
	try:
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
		order_by = request.values['order_by']
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	try:
		status = int(request.values[Wish.STATUS])
	except:
		status = 0

	if order_by != Wish.ADDED_TIME and order_by != Wish.CLICKS:
		return 'failed'
	wishes = wishdao.list_wishes(status, order_by, page, pagesize)
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.IMGS,
		Wish.USER_ID, Wish.USERNAME, Wish.DESCRIPTION, Wish.ADDED_TIME,
		Wish.MOBILE, Wish.QQ, Wish.WEIXIN, Wish.STATUS, Wish.TYPE)
	return jsonify(wishes=wishes)

@wish_blueprint.route('getWishInfo', methods=['GET', 'POST'])
def get_wish_info():
	try:
		wish_id = request.values.get(Wish.WISH_ID)
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	wish = wishdao.get_wish_info(wish_id)
	wish = dbobject2dict(wish, Wish.WISH_ID, Wish.BOOKNAME, Wish.IMGS,
		Wish.USER_ID, Wish.USERNAME, Wish.DESCRIPTION, Wish.ADDED_TIME,
		Wish.MOBILE, Wish.QQ, Wish.WEIXIN, Wish.STATUS, Wish.TYPE)
	return jsonify(wish)

@wish_blueprint.route('getWishesByUser', methods=['GET', 'POST'])
def get_wishes_by_user():
	try:
		user_id = request.values[Wish.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	wishes = wishdao.get_wishes_by_user(user_id)
	wishes = cursor2list(wishes, Wish.WISH_ID, Wish.BOOKNAME, Wish.IMGS,
		Wish.USER_ID, Wish.USERNAME, Wish.DESCRIPTION, Wish.ADDED_TIME,
		Wish.MOBILE, Wish.QQ, Wish.WEIXIN, Wish.STATUS, Wish.TYPE)
	return jsonify(wishes=wishes)

@wish_blueprint.route('setWishInfo', methods=['GET', 'POST'])
def set_wish_info():
	''' add new wish or modify wish information '''
	wish_id = request.values.get(Wish.WISH_ID)
	try:
		# wish_id = request.values[Wish.WISH_ID]
		user_id = request.values[Wish.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'

	wish_info = {}
	wish_info[Wish.USER_ID] = user_id
	for key in (Wish.USERNAME, Wish.BOOKNAME, Wish.DESCRIPTION, Wish.TYPE,\
			Wish.MOBILE, Wish.QQ, Wish.WEIXIN, Wish.STATUS):
		try:
			value = request.values[key]
		except KeyError:
			pass
		else:
			if key == Wish.STATUS or key == Wish.TYPE:
				try:
					value = int(value)
				except:
					current_app.logger.error('invalid status or type: %s' % value)
					return 'failed'
			wish_info[key] = value

	imgs = []
	for i in range(1, 4):
		try:
			f = request.values['img'+str(i)]
		except:
			break
			img = img.encode('utf-8')
			img = base64.decodestring(img)
			imgs.append(img)

	if wish_id == None or wish_id == '':
		# add new wish
		wish_id = str(uuid.uuid1())
		wish_info[Wish.WISH_ID] = wish_id
		if wishdao.insert_wish(imgs, **wish_info):
			return 'success'
		else:
			return 'failed'
	else:
		# modify wish information
		if wishdao.set_wish_info(imgs, wish_id, **wish_info):
			return 'success'
		else:
			return 'failed'

@wish_blueprint.route('setWishStatus', methods=['GET', 'POST'])
def set_wish_status():
	try:
		wish_id = request.values[Wish.WISH_ID]
		user_id = request.values[Wish.USER_ID]
		username = request.values[Wish.USERNAME]
		status = int(request.values[Wish.STATUS])
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	if wishdao.set_wish_status(wish_id, status):
		if status == 2:
			wishdao.insert_wish_token_message(str(uuid.uuid1()), user_id,\
				username, wish_id)
			scheduler.add_check_wish_status_job(wish_id)
		return 'success'
	else:
		return 'failed'
