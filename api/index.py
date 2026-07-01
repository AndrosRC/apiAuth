from flask import Blueprint, request, jsonify
from .Functions import generate_secret, update_status, get_all_records, verify_totp, delete_record

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