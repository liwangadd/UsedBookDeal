#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from controllers import *

def register_blueprint(app):
	blueprints = [
		(book_blueprint, '/book'),
		(comment_blueprint, '/comment'),
		(image_blueprint, '/img'),
		(user_blueprint, '/user'),
		(wish_blueprint, '/wish'),
	]
	for module, prefix in blueprints:
		app.register_blueprint(module, url_prefix=prefix)

def create_app():
	app = Flask(__name__)
	app.config.from_pyfile('setting.cfg')
	register_blueprint(app)
	return app

app = create_app()

if __name__ == '__main__':
	app.run()