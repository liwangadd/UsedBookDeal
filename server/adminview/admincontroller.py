# coding: utf-8

''' define the interfaces of administer '''

from flask import *
from flask.blueprints import Blueprint
from ..dao.bookdao import bookdao
from ..dao.admindao import admindao
from ..dao.fields import *
from ..utils.jsonutil import *
from ..utils.scheduler import scheduler
import uuid, base64

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@admin_blueprint.route('/')
def index():
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