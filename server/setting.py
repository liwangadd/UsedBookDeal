# coding: utf-8

''' basic settings '''

DEBUG = False
SECRET_KEY = 'usedbook_deal_app_for_school_students'
CSRF_ENABLED = True

# log file path
INFO_LOG = '../logs/info.log'
ERROR_LOG = '../logs/error.log'

# mongodb config
HOST = 'localhost'
# HOST = '120.27.51.45'
PORT = 27017
DATABASE = 'used_book_deal'

# xapian datebase path
XAPIAN_DB_PATH = 'xapian_db'

# days for users to contact offline to achieve another user's wish. the
# status of the wish will be reset 0(not achieved) if the status was not
# set 1(achieved) after that time.
WISH_DELAY = 3
# days that a book can be seen on the app before the book is set unseen
BOOK_LAST_TIME = 60