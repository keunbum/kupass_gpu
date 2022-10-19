from kupass_app import db


class Article(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    publisher = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    create_date = db.Column(db.DateTime(6), nullable=False)


class Keyword(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    activated = db.Column(db.Boolean, nullable=True)
    nickname = db.Column(db.String(255), nullable=True)
