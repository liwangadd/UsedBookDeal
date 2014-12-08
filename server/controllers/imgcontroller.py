#!/usr/bin/env python
# coding: utf-8

''' define the interfaces of image module '''

from flask import *
from flask.blueprints import Blueprint
from dao.basedao import BaseDao
from dao.fields import Image
from utils.jsonutil import *
import uuid

image_blueprint = Blueprint('image', __name__)
imagedao = BaseDao('dao_setting.cfg')

@image_blueprint.route('getUserImg', methods=['GET', 'POST'])
def get_user_img():
	try:
		user_id = request.values['user_id']
	except:
		return 'failed'
	img = imagedao.get_user_img(user_id)
	return send_file(img, add_etags=False, mimetype='image/jpeg')

@image_blueprint.route('getImg', methods=['GET', 'POST'])
def get_img():
	try:
		img_id = request.values[Image.IMG_ID]
	except:
		return 'failed'
	# if img_id == 'null':
	# 	return 'failed'
	img = imagedao.get_img(img_id)
	if not hasattr(img, 'read'):
		return None
	return send_file(img, add_etags=False, mimetype='image/jpeg')

@image_blueprint.route('deleteImg', methods=['GET', 'POST'])
def delete_img():
	try:
		img_id = request.values[Image.IMG_ID]
	except:
		return 'failed'
	imagedao.delete_img(img_id)
	return 'success'

@image_blueprint.route('getImgByBookname', methods=['GET', 'POST'])
def get_imgs_by_bookname():
	try:
		bookname = request.values[Image.BOOKNAME]
	except:
		return None
	pass