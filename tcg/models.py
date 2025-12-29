from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db=SQLAlchemy()


class Admin(db.Model):
    admin_id = db.Column(db.Integer(),primary_key=True, autoincrement=True)
    admin_username = db.Column(db.String(100),nullable=False)
    admin_email=db.Column(db.String(100),unique=True, nullable=False)
    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    admin_pwd = db.Column(db.String(255),nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password= db.Column(db.String(255), nullable=False)

class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subcategories = db.relationship('ServiceSubcategory', backref='category', cascade="all, delete-orphan", passive_deletes=True)

class ServiceSubcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id', ondelete="CASCADE"), nullable=False)


class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    contact_method = db.Column(db.String(20), nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    contact_status = db.Column(db.String(50), default="unassigned")  

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)

    assigned_staff = db.relationship("Staff", backref="contact_requests")






class QuoteRequest(db.Model):
    __tablename__ = 'quote_request'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('service_subcategory.id'), nullable=False)

    category = db.relationship('ServiceCategory', backref='quote_requests')
    subcategory = db.relationship('ServiceSubcategory', backref='quote_requests')

   
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"), nullable=True)
    assignment_status = db.Column(db.String(50), default="unassigned")  
    # "unassigned", "assigned", "in-progress", "completed"


    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=False)  # engineer, plumber, electrician
    status = db.Column(db.String(20), default="active")  # active / inactive

    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # so we can see all requests assigned to this staff
    requests = db.relationship("QuoteRequest", backref="assigned_staff", lazy=True)


class StaffActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('quote_request.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)