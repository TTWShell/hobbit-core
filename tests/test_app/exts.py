from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from hobbit_core import HobbitManager

db = SQLAlchemy()
ma = Marshmallow()

hobbit = HobbitManager()
