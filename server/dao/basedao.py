#!/usr/bin/env python
# coding: utf-8

''' define base data access class which provide file access methods and is
used for inherited by other data access class '''

from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from ConfigParser import ConfigParser
from fields import *

class BaseDao(object):
	'''@arg configfile: file name of config file '''
	def __init__(self, configfile):
		super(BaseDao, self).__init__()
		config_parser = ConfigParser()
		try:
			f = open(configfile)
			config_parser.readfp(f)
			host = config_parser.get('mongo', 'host')
			port = config_parser.getint('mongo', 'port')
			database = config_parser.get('mongo', 'database')
			self.mongo = MongoClient(host, port)
			self.db = self.mongo[database]
			self.image = self.db.image
			self.fs = GridFS(self.db, collection='img_files')
		except:
			raise
		finally:
			f.close()

	def set_img(self, img_id, f):
		img = self.image.find_one({Image.IMG_ID: img_id})
		if img == None:
			return False
		else:
			old_f_id = img.get(Image.FILE_ID)
			new_f_id = self.fs.put(f, filename=f.name)
			new_f_id = unicode(new_f_id)
			self.image.update({Image.IMG_ID: img_id}, {'$set': {Image.FILE_ID:\
				new_f_id}} )
			self.fs.delete(ObjectId(old_f_id))
			return True

	def set_img_by_object(self, object_id, f):
		img = self.image.find_one({Image.OBJECT_ID: object_id})
		if img == None:
			return False
		else:
			old_f_id = img.get(Image.FILE_ID)
			new_f_id = self.fs.put(f, filename=f.name)
			new_f_id = unicode(new_f_id)
			self.image.update({Image.OBJECT_ID:object_id}, \
				{'$set': {Image.FILE_ID:new_f_id}} )
			self.fs.delete(old_f_id)
			return True

	def insert_img(self, img_id, f, object_id, bookname=None, category=1):
		file_id = img.fs.put(f, filename=f.name)
		file_id = unicode(file_id)
		if bookname == None:
			self.image.insert({Image.IMG_ID: img_id, Image.OBJECT_ID: \
				object_id, Image.CATEGORY: category, Image.FILE_ID: file_id})
		else:
			self.image.insert({Image.IMG_ID: img_id, Image.OBJECT_ID: \
				Image.BOOKNAME: bookname, object_id, Image.CATEGORY: category,\
				Image.FILE_ID: file_id})
		return True

	def delete_img(self, img_id):
		# only images inserted by user can be deleted
		img = self.image.find_one({Image.IMG_ID: img_id, Image.CATEGORY: 1})
		if img != None:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			self.fs.delete(f_id)
			self.image.remove({Image.IMG_ID: img_id, Image.CATEGORY: 1})
		return True

	def delete_img_by_object(self, object_id):
		cursor = self.image.find({Image.OBJECT_ID:object_id, Image.CATEGORY:1})
		for img in cursor:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			self.fs.delete(f_id)
		self.image.remove({Image.OBJECT_ID:object_id, Image.CATEGORY:1})

	def get_img(self, img_id):
		img = self.image.find_one({Image.IMG_ID: img_id})
		if img == None:
			return None
		else:
			f_id = img.get(Image.FILE_ID)
			f_id = ObjectId(f_id)
			return self.fs.get(f_id)

	def get_imgs_by_bookname(self, bookname, limit):
		pass
