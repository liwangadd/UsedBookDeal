
#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from logging.handlers import RotatingFileHandler
from controllers import user_blueprint, book_blueprint, wish_blueprint, comment_blueprint, image_blueprint
from werkzeug.contrib.fixers import ProxyFix
import base64, os, logging, sys

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '.')

def register_blueprint(app):
	blueprints = [
		(book_blueprint, '/book/'),
		(comment_blueprint, '/comment/'),
		(image_blueprint, '/img/'),
		(user_blueprint, '/user/'),
		(wish_blueprint, '/wish/'),
	]
	for module, prefix in blueprints:
		app.register_blueprint(module, url_prefix=prefix)

def config_logging(app):
	info_log = os.path.join(app.root_path, app.config['INFO_LOG'])
	error_log = os.path.join(app.root_path, app.config['ERROR_LOG'])

	formatter = logging.Formatter(
	'''%(asctime)s %(levelname)s [in %(pathname)s:%(lineno)d]:
	%(message)s ''')

	if app.debug == True:
		info_handler = RotatingFileHandler(info_log, maxBytes=102400, backupCount=10)
		info_handler.setLevel(logging.INFO)
		info_handler.setFormatter(formatter)
		app.logger.addHandler(info_handler)

	error_handler = RotatingFileHandler(error_log, maxBytes=102400,
		backupCount=10)
	error_handler.setLevel(logging.ERROR)
	error_handler.setFormatter(formatter)
	app.logger.addHandler(error_handler)

def create_app():
	app = Flask(__name__)
	app.config.from_pyfile('setting.py')
	register_blueprint(app)
	config_logging(app)
	app.wsgi_app = ProxyFix(app.wsgi_app)
	return app

app = create_app()

@app.route('/')
def function():
	return 'hello'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)