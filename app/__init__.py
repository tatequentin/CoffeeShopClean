from flask import Flask

def create_app():
	app = Flask(__name__)
	app.secret_key = 'super_secret_key' # can change to something for entire group

	from . import routes
	app.register_blueprint(routes.bp)

	return app

