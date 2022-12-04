from flask import render_template, Blueprint

input_blueprint = Blueprint('input_bp', __name__, template_folder='templates')


@input_blueprint.route("/input")
def input():
    return render_template('input.html')
