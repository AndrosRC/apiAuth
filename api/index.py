import os
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Importamos la instancia de db desde extensions
from .extensions import db
# Importamos las funciones
from .Functions import generate_secret, update_status, get_all_records, verify_totp, delete_record

load_dotenv()

# Inicialización de la App
app = Flask(__name__)
CORS(app)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos con la app
db.init_app(app)

# Definición del Blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/request', methods=['POST'])
def handle_request():
    return jsonify(generate_secret(request.json))

@api_bp.route('/api/records', methods=['GET'])
def handle_records():
    return jsonify(get_all_records())

@api_bp.route('/api/revoke/<int:id>', methods=['POST'])
def handle_revoke(id):
    return jsonify(update_status(id, 'Revocado'))

@api_bp.route('/api/delete/<int:id>', methods=['DELETE'])
def handle_delete(id):
    return jsonify(delete_record(id))

@api_bp.route('/api/verify', methods=['POST'])
def handle_verify():
    data = request.json
    result = verify_totp(data.get('id'), data.get('pin'))
    return jsonify(result), (200 if result['success'] else 400)

# Registramos el blueprint
app.register_blueprint(api_bp)