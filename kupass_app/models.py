from kupass_app import db


class Article(db.Model):
    article_id = db.Column(db.BigInteger, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    content = db.Column(db.String(255), nullable=True)
    create_date = db.Column(db.DateTime(6), nullable=True)
    publisher = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)

class Keyword(db.Model):
    keyword_id = db.Column(db.BigInteger, primary_key=True)
    keyword = db.Column(db.String(255), nullable=True)
    article_id = db.Column(db.BigInteger, nullable=True)

