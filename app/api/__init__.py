from flask import Blueprint

""" This module registers an api blueprint for 
the application.
"""

bp = Blueprint('api', __name__)

from app.api import users, errors, tokens