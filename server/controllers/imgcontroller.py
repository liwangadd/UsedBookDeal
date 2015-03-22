#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of image module '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.basedao import basedao as imagedao
from ..dao.fields import Image, User
from ..utils.jsonutil import *
import uuid

image_blueprint = Blueprint('image', __name__)

@image_blueprint.route('getUserImg', methods=['GET', 'POST'])
def get_user_img():
	try:
		user_id = request.values[User.USER_ID]
		assert user_id != ''
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	img = imagedao.get_user_img(user_id)
	try:
		assert img is not None
	except AssertionError:
		# current_app.logger.error('did not found the image of user(%s)' % user_id)
		return 'failed'
	return send_file(img, add_etags=False, mimetype='image/jpeg')

@image_blueprint.route('getImg', methods=['GET', 'POST'])
def get_img():
	try:
		img_id = request.values[Image.IMG_ID]
		assert img_id != ''
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	img = imagedao.get_img(img_id)
	if not hasattr(img, 'read'):
		# current_app.logger.error('invalid image file. img_id: %s' % img_id)
		return 'failed'
	return send_file(img, add_etags=False, mimetype='image/jpeg')

@image_blueprint.route('deleteImg', methods=['GET', 'POST'])
def delete_img():
	try:
		img_id = request.values[Image.IMG_ID]
	except KeyError:
		current_app.logger.error('invalid args')
		return 'failed'
	imagedao.delete_img(img_id)
	return 'success'

@image_blueprint.route('getImgByBookname', methods=['GET', 'POST'])
def get_imgs_by_bookname():
	try:
		bookname = request.values[Image.BOOKNAME]
		limit = int(request.values['limit'])
	except:
		current_app.logger.error('invalid args')
		return 'failed'
	imgs = imagedao.get_imgs_by_bookname(bookname, limit)
	# imgs = cursor2list(imgs, Image.IMG_ID)
	return jsonify(imgs=imgs)
