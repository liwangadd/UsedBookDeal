#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.insert(0, '/home/clint/py/projects/UsedBookDeal/server/')

from dao.basedao import BaseDao
from dao.userdao import UserDao
from dao.bookdao import BookDao
from dao.wishdao import WishDao
from dao.commentdao import CommentDao
from dao.fields import *
from uuid import uuid1

def userdao_test():
	userdao = UserDao('../dao_setting.cfg')
	user_id = str(uuid1())
	password = 'testpassword'
	assert userdao.insert_user(user_id, password)
	assert userdao.check_login(user_id, password)
	assert not userdao.check_login(user_id, 'password')
	assert not userdao.check_login('test user id', 'password')
	user_info = { User.USERNAME: 'testusername', User.GENDER: 1,
		User.MOBILE: 'mobile' }
	assert userdao.set_user_info(user_id, **user_info)
	user_info2 = userdao.get_user_info(user_id)
	assert user_info[User.USERNAME] == user_info2[User.USERNAME] and user_info[User.GENDER] == user_info2[User.GENDER] and user_info[User.MOBILE] == user_info[User.MOBILE]
	user_info3 = userdao.get_user_info('user_id')
	assert user_info3 is None

def bookdao_test():
	bookdao = BookDao('../dao_setting.cfg')
	f = open('img.jpg')
	book_info = {}
	book_id = str(uuid1())
	user_id = '48ac1366-7cf2-11e4-b8a5-642737f58199'
	book_info[Book.BOOK_ID] = book_id
	book_info[Book.BOOKNAME] = 'testbookname'
	book_info[Book.PRICE] = 10
	book_info[Book.USER_ID] = user_id
	book_info[Book.TYPE] = 0
	book_info[Book.USERNAME] = 'testusername'
	book_info[Book.NEWNESS] = 'testnewness'
	book_info[Book.AUDIENCE] = 'audience'
	book_info[Book.DESCRIPTION] = 'description'
	book_info[Book.MOBILE] = 'mobile'
	book_info[Book.QQ] = 'qq'
	book_info[Book.WEIXIN] = 'weixin'
	assert bookdao.insert_book([f], **book_info)
	book_info[Book.DESCRIPTION] = 'test description'
	assert bookdao.set_book_info(book_id, \
		description=book_info[Book.DESCRIPTION])
	result = bookdao.get_book_info(book_id)
	for key


if __name__ == '__main__':
	userdao_test()

