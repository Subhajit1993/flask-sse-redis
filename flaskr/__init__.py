from flask import Flask
from flask_sse import sse


def create_app(config=None):
    # create and configure the app
    app = Flask(__name__)
    if config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_object(config)

    # Routes and Controllers
    from flaskr.controllers.home import home_bp
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(sse, url_prefix='/stream')
    return app
