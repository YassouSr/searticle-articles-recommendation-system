from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import func

bcrypt = Bcrypt()
db = SQLAlchemy()


class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(10), nullable=False)
    last_name = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = self.generate_hash_password(
            password
        )  # save password in hash format for security

    def __repr__(self):
        return "<User {} {}>".format(self.first_name, self.last_name)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def generate_hash_password(self, value):
        return bcrypt.generate_password_hash(value).decode("utf8")


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    link = db.Column(db.Text)
    authors = db.Column(db.Text)
    references = db.Column(ARRAY(db.Integer))
    year = db.Column(db.Integer)

    def __repr__(self):
        return "<Article ({}, '{}')>".format(self.id, self.title)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id", ondelete="CASCADE"))
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))
    article_title = db.Column(db.Text, nullable=False)
    seen_on = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)

    def __repr__(self):
        return "<History ({}, '{}')>".format(self.profile_id, self.article_id)
