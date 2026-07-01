from .models import AuthRequest
from .extensions import db
import pyotp
from sqlalchemy import desc
from datetime import datetime, timedelta

def revoke_existing_pending(user_email):
    # Revoca registros Pendientes previos del mismo usuario al crear uno nuevo
    AuthRequest.query.filter_by(user_email=user_email, status='Pendiente')\
        .update({"status": 'Revocado'})
    db.session.commit()

def generate_secret(data):
    # Antes de generar uno nuevo, limpiamos pendientes previos del usuario
    revoke_existing_pending(data['user_email'])
    
    secret = pyotp.random_base32()
    new_req = AuthRequest(
        service_name=data['service_name'],
        user_email=data['user_email'],
        secret_key=secret
    )
    db.session.add(new_req)
    db.session.commit()
    return {"id": new_req.id, "secret": secret}

def get_all_records():
    
    reqs = AuthRequest.query.order_by(desc(AuthRequest.created_at)).all()
    return [
        {
            "id": r.id, 
            "service_name": r.service_name, 
            "user_email": r.user_email, 
            "status": r.status,
            "created_at": r.created_at.isoformat() + "Z" if r.created_at else ""
        } for r in reqs
    ]

def update_status(id, status):
    req = AuthRequest.query.get(id)
    if req:
        req.status = status
        db.session.commit()
        return {"message": "Actualizado"}
    return {"message": "Registro no encontrado"}

def verify_totp(record_id, pin):
    req = AuthRequest.query.get(record_id)
    
    if not req:
        return {"success": False, "message": "Registro no encontrado"}
    
    totp = pyotp.TOTP(req.secret_key)
    
    if totp.verify(pin):
        req.status = 'Verificado'
        db.session.commit()
        return {"success": True, "message": "Autenticador vinculado correctamente"}
    else:
        return {"success": False, "message": "Código incorrecto o expirado"}

def delete_record(id):
    req = AuthRequest.query.get(id)
    if req:
        db.session.delete(req)
        db.session.commit()
        return {"success": True, "message": "Registro eliminado completamente"}
    return {"success": False, "message": "No encontrado"}