# coding: utf-8

import xapian
from mmseg.search import seg_txt_2_dict, seg_txt_search
from ..dao.fields import Book
from ..dao.basedao import basedao
from ..setting import XAPIAN_DB_PATH

def _fields_txt_2_dict(*txts):
	txt = u' '.join(txts)
	txt = txt.encode('utf-8')
	# print txt
	return seg_txt_2_dict(txt)


class XapianTool(object):
	"""define index and search methods"""
	def __init__(self, db_path, dao):
		super(XapianTool, self).__init__()
		self.db_path = db_path
		self.dao = dao
		self.index()
		self.read_only_db = xapian.Database(db_path)
		self.enquire = xapian.Enquire(self.read_only_db)
		# self.index()

	def index(self):
		self.wirtable_db = xapian.WritableDatabase(self.db_path,
					xapian.DB_CREATE_OR_OVERWRITE)
		cursor = self.dao.book.find({Book.STATUS: 0})
		for book in cursor:
			fields = []
			fields.append(book[Book.BOOKNAME])
			for key in (Book.NEWNESS, Book.DESCRIPTION, Book.AUDIENCE):
				try:
					fields.append(book[key])
				except KeyError:
					pass
			self.set_document(book[Book.BOOK_ID], *fields)
		self.wirtable_db.flush()
		self.wirtable_db.close()

	def set_document(self, book_id, *fields):
		doc = xapian.Document()
		doc.set_data(book_id)

		term_dict = _fields_txt_2_dict(*fields)
		for key, value in term_dict.iteritems():
			# print key, value
			doc.add_term(key, value)

		self.wirtable_db.replace_document(book_id, doc)

	# def delete_document(self, book_id):
	# 	self.db.delete_document(book_id)

	def search(self, keywords, page, limit):
		query_list = []
		for key, value in seg_txt_2_dict(keywords).iteritems():
			query = xapian.Query(key, value)
			query_list.append(query)

		if len(query_list) == 1:
			query = query_list[0]
		else:
			query = xapian.Query(xapian.Query.OP_OR, query_list)

		self.enquire.set_query(query)
		offset = (page - 1) * limit
		matches = self.enquire.get_mset(offset, limit)

		book_ids = []
		for m in matches:
			book_ids.append(m.document.get_data())
		return book_ids

xapian_tool = XapianTool(XAPIAN_DB_PATH, basedao)