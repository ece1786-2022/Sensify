from flask import Flask

from app.input.input import input_blueprint
from app.result.result import result_blueprint
from app.login.login import login_blueprint


def create_app():
    """
    Creating and returning the app
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'JUSTARANDOMKEY'

    app.register_blueprint(login_blueprint)
    app.register_blueprint(input_blueprint)
    app.register_blueprint(result_blueprint)
    return app
