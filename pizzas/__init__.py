from flask import Blueprint

pizzas = Blueprint(
    'pizzas',
    __name__,
    template_folder='templates'
)

from . import routes
