from flask import Flask
from flask_graphql import GraphQLView

from diskuze.config import config
from diskuze.models import db
from diskuze.schema import schema

app = Flask(__name__)

app.config.from_object(config)

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))
