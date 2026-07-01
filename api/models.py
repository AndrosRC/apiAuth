from . import db
import datetime

class AuthRequest(db.Model):
    __tablename__ = 'auth_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    secret_key = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(50), default='Pendiente')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)