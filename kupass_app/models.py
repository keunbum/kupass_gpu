from kupass_app import db


class Article(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    content = db.Column(db.String(255), nullable=False)
    create_date = db.Column(db.DateTime(6), nullable=True)
    publisher = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=False)

class Keyword(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.String(255), nullable=True)

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    activated = db.Column(db.Boolean, nullable=True)
    nickname = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)

