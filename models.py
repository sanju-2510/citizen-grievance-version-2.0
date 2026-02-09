from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') # user, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    aadhaar = db.Column(db.String(12), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Submitted') # Submitted, Assigned, In Progress, Resolved
    cluster_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    evidence_path = db.Column(db.String(200), nullable=True)

class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.String(50), unique=True, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    complaint_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Active')
