from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from datetime import datetime
from database import init_db, db
from lot import Lot

app = Flask(__name__)

# Configuration de la base de données PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/lots_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données
init_db(app)

api = Api(app, version="1.0", title="Lot Quality Control API", description="API pour gérer et contrôler la qualité des lots pharmaceutiques")

# Drapeau d'initialisation de la base de données
initialized = False  

# Modèle pour l'API Swagger (Flask-RESTX)
lot_model = api.model('Lot', {
    'product_name': fields.String(required=True, description='Nom du produit'),
    'quantity': fields.Integer(required=True, description='Quantité produite'),
    'production_date': fields.String(required=True, description='Date de production (YYYY-MM-DD)'),
    'expiration_date': fields.String(required=True, description='Date de péremption (YYYY-MM-DD)')
})

def seed_database():
    """Insérer des lots par défaut dans la base de données."""
    lots = [
        Lot("Paracetamol 500mg", 1000, "2023-01-01", "2024-01-01"),
        Lot("Ibuprofen 200mg", 500, "2023-02-01", "2024-02-01"),
        Lot("Aspirin 100mg", 2000, "2022-11-15", "2023-11-15"),
        Lot("Vitamin C 1000mg", 1500, "2023-03-10", "2025-03-10"),
        Lot("Amoxicillin 250mg", 800, "2022-12-01", "2024-12-01"),
        Lot("Cough Syrup 100ml", 600, "2023-04-05", "2025-04-05"),
        Lot("Cetirizine 10mg", 1200, "2022-10-20", "2023-10-20"),
        Lot("Metformin 500mg", 1800, "2023-05-15", "2024-05-15"),
        Lot("Omeprazole 20mg", 900, "2023-06-01", "2025-06-01"),
        Lot("Loratadine 10mg", 1000, "2023-07-12", "2024-07-12"),
    ]
    
    for lot in lots:
        db.session.add(lot)
    db.session.commit()
    print("Database seeded with initial lots.")

@app.before_request
def initialize():
    """Initialiser la base de données une seule fois avant la première requête."""
    global initialized
    if not initialized:
        db.create_all()
        # Vérifier si la base est déjà peuplée
        if Lot.query.count() == 0:
            seed_database()
        initialized = True

# Définition des endpoints avec Flask-RESTX
@api.route('/lots')
class LotList(Resource):
    @api.doc('list_lots')
    def get(self):
        """Retourne la liste de tous les lots."""
        lots = Lot.query.all()
        output = []
        for lot in lots:
            lot_data = {
                'lot_id': lot.lot_id,
                'product_name': lot.product_name,
                'quantity': lot.quantity,
                'production_date': lot.production_date.strftime('%Y-%m-%d'),
                'expiration_date': lot.expiration_date.strftime('%Y-%m-%d')
            }
            output.append(lot_data)
        return jsonify({'lots': output})

    @api.expect(lot_model)
    def post(self):
        """Crée un nouveau lot."""
        data = request.get_json()
        new_lot = Lot(
            product_name=data['product_name'],
            quantity=data['quantity'],
            production_date=data['production_date'],
            expiration_date=data['expiration_date']
        )
        db.session.add(new_lot)
        db.session.commit()
        return jsonify({'message': 'Lot created successfully'}), 201

@api.route('/lots/<int:lot_id>')
class LotResource(Resource):
    @api.doc('get_lot')
    def get(self, lot_id):
        """Retourne les détails d'un lot spécifique."""
        lot = Lot.query.get_or_404(lot_id)
        lot_data = {
            'lot_id': lot.lot_id,
            'product_name': lot.product_name,
            'quantity': lot.quantity,
            'production_date': lot.production_date.strftime('%Y-%m-%d'),
            'expiration_date': lot.expiration_date.strftime('%Y-%m-%d')
        }
        return jsonify({'lot': lot_data})

    @api.doc('delete_lot')
    def delete(self, lot_id):
        """Supprime un lot."""
        lot = Lot.query.get_or_404(lot_id)
        db.session.delete(lot)
        db.session.commit()
        return jsonify({'message': 'Lot deleted successfully'}), 200

@api.route('/compliant_lots')
class CompliantLots(Resource):
    @api.doc('get_compliant_lots')
    def get(self):
        """Retourne la liste de tous les lots conformes."""
        today = datetime.now().date()
        compliant_lots = Lot.query.filter(Lot.expiration_date >= today).all()
        
        output = []
        for lot in compliant_lots:
            lot_data = {
                'lot_id': lot.lot_id,
                'product_name': lot.product_name,
                'quantity': lot.quantity,
                'production_date': lot.production_date.strftime('%Y-%m-%d'),
                'expiration_date': lot.expiration_date.strftime('%Y-%m-%d')
            }
            output.append(lot_data)
        
        return jsonify({'compliant_lots': output})

@api.route('/compliant_percentage')
class CompliantPercentage(Resource):
    @api.doc('get_compliant_percentage')
    def get(self):
        """Retourne le pourcentage de lots conformes."""
        total_lots = Lot.query.count()
        compliant_lots = Lot.query.filter(Lot.expiration_date >= datetime.now().date()).count()

        if total_lots == 0:
            percentage = 0.0
        else:
            percentage = (compliant_lots / total_lots) * 100

        return jsonify({'compliant_percentage': percentage})

@api.route('/expired_lots')
class ExpiredLots(Resource):
    @api.doc('get_expired_lots')
    def get(self):
        """Retourne la liste de tous les lots périmés."""
        today = datetime.now().date()
        expired_lots = Lot.query.filter(Lot.expiration_date < today).all()
        
        output = []
        for lot in expired_lots:
            lot_data = {
                'lot_id': lot.lot_id,
                'product_name': lot.product_name,
                'quantity': lot.quantity,
                'production_date': lot.production_date.strftime('%Y-%m-%d'),
                'expiration_date': lot.expiration_date.strftime('%Y-%m-%d')
            }
            output.append(lot_data)
        
        return jsonify({'expired_lots': output})

        
# Point d'entrée principal
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
