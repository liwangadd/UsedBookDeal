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
		wishtype = int(request.values[Wish.TYPE])
	except:
		current_app.logger.error('invalid args')
		return 'failed'

	try:
		status = int(request.values[Wish.STATUS])
	except:
		status = 0

	try:
		order_by = request.values['order_by']
		assert order_by == Wish.ADDED_TIME or order_by == Wish.CLICKS
	except:
		order_by = Wish.ADDED_TIME

	wishes = wishdao.list_wishes(status, wishtype, order_by, page, pagesize)
	wishes = cursor2list(wishes, *Wish.ALL)
	return jsonify(wishes=wishes)

@wish_blueprint.route('getWishInfo', methods=['GET', 'POST'])
def get_wish_info():
	try:
		wish_id = request.values.get(Wish.WISH_ID)
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	wish = wishdao.get_wish_info(wish_id)
	wish = dbobject2dict(wish, *Wish.ALL)
	return jsonify(wish)

@wish_blueprint.route('getWishesByUser', methods=['GET', 'POST'])
def get_wishes_by_user():
	try:
		user_id = request.values[Wish.USER_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	wishes = wishdao.get_wishes_by_user(user_id)
	wishes = cursor2list(wishes, *Wish.ALL)
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
	for key in Wish.ALL:
		try:
			value = request.values[key]
		except KeyError:
			pass
		else:
			if key == Wish.WISH_ID:
				continue
			elif key == Wish.STATUS:
				try:
					value = int(value)
					assert value == 0 or value == 1 or value == 2
				except:
					current_app.logger.error('invalid status: %s' % value)
					return 'failed'
			elif key == Wish.TYPE:
				try:
					value = int(value)
					assert value >= 0 and value <= 6
				except:
					current_app.logger.error('invalid type: %s' % value)
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
			current_app.logger.error('error in insert_wish')
			return 'failed'
	else:
		# modify wish information
		if wishdao.set_wish_info(imgs, wish_id, **wish_info):
			return 'success'
		else:
			current_app.logger.error('error in set_wish_info')
			return 'failed'

@wish_blueprint.route('setWishStatus', methods=['GET', 'POST'])
def set_wish_status():
	try:
		wish_id = request.values[Wish.WISH_ID]
		user_id = request.values[Wish.USER_ID]
		username = request.values[Wish.USERNAME]
		status = int(request.values[Wish.STATUS])
		assert status == 0 or status == 1 or status == 2
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

@wish_blueprint.route('wishClicked', methods=['GET', 'POST'])
def wish_clicked():
	try:
		wish_id = request.values[Wish.WISH_ID]
	except:
		current_app.logger.errork('invalid args')
		return 'failed'
	if wishdao.wish_clicks_plus(wish_id):
		return 'success'
	else:
		return 'failed'