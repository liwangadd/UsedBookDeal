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

# @admin_blueprint.before_request
# def interceptor():
# 	print str(request.url_rule)
# 	print (str(request.url_rule == '/admin//'))
# 	if str(request.url_rule) != '/admin//':
# 		if session.get('admin_id') is None:
# 			return redirect(url_for('admin.login'))

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
	# total_num = users.count()
	total_num = admindao.count_user()
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
	# total_num = wishes.count()
	total_num = admindao.count_wish()
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
	# total_num = comments.count()
	total_num = len(comments)
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
	# total_num = books.count()
	total_num = admindao.count_book(type)
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
	# total_num = comments.count()
	total_num = len(comments)
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('bookinfo.html', book = book, comments = comments, total_page = total_page, page = page)

@admin_blueprint.route('searchBook', methods=['POST', 'GET'])
def search_book():
	try:
		keyword = request.values['keyword']
		page = int(request.values['page'])
		pagesize = int(request.values['pagesize'])
	except:
		return 'invalid args'

	try:
		booktype = request.values[Book.TYPE]
		assert booktype != ''
	except:
		booktype = 0
	else:
		try:
			booktype = int(booktype)
		except:
			return 'invalid booktype: %s' % booktype

	keywords = keyword.split(' ')
	books = bookdao.search_book(keywords, page, pagesize, booktype)
	# total_num = books.count()
	total_num = len(books)
	total_page = (total_num + pagesize - 1) / pagesize
	return render_template('searchbook.html', books = books, page = page,
		total_page = total_page, keyword = keyword, type = booktype)

@admin_blueprint.route('insertDefaultImg', methods=['POST', 'GET'])
def insert_default_img():
	pass

@admin_blueprint.route('insertDefaultImgAction', methods=['POST', 'GET'])
def insert_default_img_action():
	pass

@admin_blueprint.route('sendMessage', methods=['POST', 'GET'])
def send_messages():
	return render_template('sendmessage.html')

@admin_blueprint.route('sendMessagesToAll', methods=['POST', 'GET'])
def send_messages_to_all():
	try:
		content = request.values['content']
	except:
		return 'invalid args'

	userdao.insert_system_message_to_all(content)
	return redirect(url_for('admin.list_users'))

@admin_blueprint.route('sendMessagesToOne', methods=['POST', 'GET'])
def send_messages_to_one():
	try:
		content = request.values['content']
		user_id = request.values['user_id']
	except:
		return 'invalid args'

	message_id = str(uuid.uuid1())
	if userdao.insert_system_message_to_one(message_id, user_id, content):
		return redirect(url_for('admin.list_users'))
	else:
		return 'invalid user_id'