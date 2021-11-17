from flask import Blueprint, render_template, redirect, flash

main_blueprint = Blueprint(
    'main', 
    __name__,
    template_folder='../templates/main'
)

@main_blueprint.route('/', methods=['GET'])
def index():
    return render_template('main.html')

# That's all!
