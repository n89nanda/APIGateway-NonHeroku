"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')


import APIGateway_flask.views
