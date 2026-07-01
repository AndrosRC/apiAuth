import socket

# Corrección en la lógica de forzado a IPv4
def force_ipv4_socket():
    original_getaddrinfo = socket.getaddrinfo
    def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # Si la familia es AF_INET6 (valor 10), la forzamos a AF_INET (valor 2)
        if family == socket.AF_INET6:
            family = socket.AF_INET
        return original_getaddrinfo(host, port, family, type, proto, flags)
    socket.getaddrinfo = ipv4_getaddrinfo

force_ipv4_socket()

import os
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from .extensions import db
from .Functions import generate_secret, update_status, get_all_records, verify_totp, delete_record

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de base de datos con optimizaciones para Serverless
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_size": 1,
    "max_overflow": 0,
    "pool_pre_ping": True,
    "connect_args": {"connect_timeout": 10}
}

db.init_app(app)

# Definición del Blueprint
api_bp = Blueprint('api', __name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de Autenticacion funcionando correctamente"}), 200

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

app.register_blueprint(api_bp)