from sqlalchemy import func

from . import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    card_number = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    card_balance = db.Column(db.Float, nullable=False)
    sent_transfers = db.relationship('Transfer', foreign_keys='Transfer.sender_card', backref='sender', lazy=True, cascade='all,delete')
    received_transfers = db.relationship('Transfer', foreign_keys='Transfer.recipient_card', backref='recipient', lazy=True, cascade='all,delete')

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_card = db.Column(db.String(50), db.ForeignKey('users.card_number'), nullable=False)
    recipient_card = db.Column(db.String(50), db.ForeignKey('users.card_number'), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    transfer_time = db.Column(db.DateTime, nullable=False,default=func.now())