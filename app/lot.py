from datetime import datetime
from database import db

class Lot(db.Model):
    lot_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    production_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)

    def __init__(self, product_name, quantity, production_date, expiration_date):
        self.product_name = product_name
        self.quantity = quantity
        self.production_date = datetime.strptime(production_date, '%Y-%m-%d').date()
        self.expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
