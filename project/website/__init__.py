from flask import Flask

"""
define parameters of the app
@return app
"""
def app_create():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'somethingsomething'

    from .views import coisa

    app.register_blueprint(coisa, url_prefix='/')

    return app
