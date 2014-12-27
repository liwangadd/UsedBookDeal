#!/usr/bin/env python
# coding: utf-8

from ..dao.wishdao import wishdao
from ..dao.bookdao import bookdao
from apscheduler.schedulers.background import BackgroundScheduler
from xapiansearch import xapian_tool
from datetime import datetime, timedelta
from .. import setting

def _reset_wish_status(wish_id):
	wishdao.reset_wish_status(wish_id)

def _set_book_removed(book_id):
	bookdao.set_book_status(book_id, 2)

class MyScheduler(object):
	"""scheduler class, difine scheduler and jobs"""
	def __init__(self):
		super(MyScheduler, self).__init__()
		self.scheduler = BackgroundScheduler()
		self.wish_time = setting.WISH_DELAY
		self.book_time = setting.BOOK_LAST_TIME

	def start(self):
		self.scheduler.start()

	def shutdown(self):
		self.scheduler.shutdown()

	def add_check_wish_status_job(self, wish_id):
		print datetime.now()
		run_date = datetime.now() + timedelta(seconds=self.wish_time)
		self.scheduler.add_job(_reset_wish_status, 'date', args=[wish_id],
			run_date=run_date)

	def add_set_book_removed_job(self, book_id):
		run_date = datetime.now() + timedelta(days=self.book_time)
		self.scheduler.add_job(_set_book_removed, 'date', args=[book_id],
			run_date=run_date)

	def add_xapian_reindex_job(self, xapian_tool):
		self.scheduler.add_job(xapian_tool.index, 'interval', minutes=5)

scheduler = MyScheduler()
scheduler.add_xapian_reindex_job(xapian_tool)
scheduler.start()