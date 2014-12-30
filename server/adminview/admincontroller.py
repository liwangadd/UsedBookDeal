# coding: utf-8

''' define the interfaces of administer '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.userdao import userdao
from ..dao.bookdao import bookdao
from ..dao.wishdao import wishdao
from ..dao.commentdao import commentdao
from ..dao.admindao import admindao
from ..dao.fields import *
from ..utils.jsonutil import *
from ..utils.scheduler import scheduler
import uuid, base64

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@admin_blueprint.before_request
def interceptor():
	if str(request.url_rule) != '/admin//':
		if session.get('admin_id') is None:
			return redirect(url_for('login'))

@admin_blueprint.route('/')
def login():
	return render_template('index.html')

@admin_blueprint.route('loginAction', methods=['POST', 'GET'])
def login_action():
	try:
		admin_id = request.values[Admin.ADMIN_ID]
		password = request.values[Admin.PASSWORD]
	except:
		return 'invalid args'
	if admindao.check_login(admin_id, password):
		session['admin_id'] = admin_id
		return redirect(url_for('admin.list_users'))
	else:
		return render_template('index.html', err_info='wrong id or password')

@admin_blueprint.route('set_info', methods=['GET', 'POST'])
def set_info():
	try:
		admin_id = request.values[Admin.ADMIN_ID]
		password = request.values[Admin.PASSWORD]
		new_password = request.values['newpassword']
	except:
		return 'invalid args'

@admin_blueprint.route('userList')
def list_users():
	try:
		page = int(request.values['page'])
	except:
		page = 1
	try:
		pagesize = int(request.values['pagesize'])
	except:
		pagesize = 20

	users = admindao.list_users(page, pagesize)
	total_num = users.count()
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('userlist.html', users = users,
		total_page = total_page, page = page)

@admin_blueprint.route('userInfo')
def show_user_info():
	try:
		user_id = request.values[User.USER_ID]
	except:
		return 'invalid args'
	user = userdao.get_user_info(user_id)
	messages = userdao.get_messages_by_user(user_id)
	return render_template('userinfo.html', user = user, messages = messages)

@admin_blueprint.route('wishList')
def list_wishes():
	try:
		page = int(request.values['page'])
	except:
		page = 1
	try:
		pagesize = int(request.values['pagesize'])
	except:
		pagesize = 20

	wishes = admindao.list_wishes(page, pagesize)
	total_num = wishes.count()
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('wishlist.html', wishes = wishes,
		total_page = total_page, page = page)

@admin_blueprint.route('wishInfo')
def show_wish_info():
	try:
		wish_id = request.values[Wish.WISH_ID]
	except:
		return 'invalid args'
	# comments' page and pagesize
	try:
		page = int(request.values['page'])
	except:
		page = 1
	try:
		pagesize = int(request.values['pagesize'])
	except:
		pagesize = 20
	wish = wishdao.get_wish_info(wish_id)
	comments = commentdao.get_comments_by_object(wish_id, page, pagesize)
	total_num = comments.count()
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('wishinfo.html', wish = wish, comments = comments,
		total_page = total_page, page = page)

@admin_blueprint.route('bookList')
def list_books():
	try:
		page = int(request.values['page'])
	except:
		page = 1
	try:
		pagesize = int(request.values['pagesize'])
	except:
		pagesize = 20
	try:
		type = int(request.values[Book.TYPE])
	except:
		type = 1
	try:
		sort = request.values['sort']
		assert sort == Book.BOOKNAME or sort == Book.ADDED_TIME or \
			sort == Book.CLICKS
	except:
		sort = Book.BOOKNAME

	books = admindao.list_books(type, sort, page, pagesize)
	total_num = books.count()
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('booklist.html', books = books, type = type,
		sort = sort, page = page, total_page = total_page)

@admin_blueprint.route('bookInfo')
def show_book_info():
	try:
		book_id = request.values[Book.BOOK_ID]
	except:
		return 'invalid args'
	# comments' page and pagesize
	try:
		page = int(request.values['page'])
	except:
		page = 1
	try:
		pagesize = int(request.values['pagesize'])
	except:
		pagesize = 20
	book = bookdao.get_book_info(book_id)
	comments = commentdao.get_comments_by_object(book_id, page, pagesize)
	total_num = comments.count()
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('bookinfo.html', book = book, comments = comments, total_page = total_page, page = page)