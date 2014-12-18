# coding: utf-8

import xapian
from mmseg.search import seg_txt_2_dict, seg_txt_search
from dao.fields import Book
from dao.basedao import basedao
from setting import XAPIAN_DB_PATH

def _fields_txt_2_dict(*txts):
	return seg_txt_2_dict(u' '.join(txts))


class XapianTool(object):
	"""define index and search methods"""
	def __init__(self, db_path, dao):
		super(XapianTool, self).__init__()
		self.db = xapian.WritableDatabase(db_path, xapian.DB_CREATE_OR_OPEN)
		self.enquire = xapian.Enquire(self.db)
		self.dao = dao

	def index(self):
		cursor = self.dao.book.find({Book.STATUS: 1})
		for book in cursor:
			self.set_document(book[Book.BOOK_ID], book[Book.BOOKNAME],
				book[Book.NEWNESS], book[Book.AUDIENCE],
				book[Book.DESCRIPTION])
		self.db.flush()

	def set_document(self, book_id, *fields):
		doc = xapian.Document()
		dos.set_data(book_id)

		term_dict = _fields_txt_2_dict(*fields)
		for key, value in term_dict.iteritems():
			doc.add_term(key, value)

		self.db.replace_document(book_id, doc)

	def flush(self):
		self.db.flush()

	def delete_document(self, book_id):
		self.db.delete_document(book_id)

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