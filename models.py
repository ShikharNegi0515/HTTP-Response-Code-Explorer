from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    response_codes = db.Column(db.Text, nullable=False)  # JSON string
    image_links = db.Column(db.Text, nullable=False)     # JSON string
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
