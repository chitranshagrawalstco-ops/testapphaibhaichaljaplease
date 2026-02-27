import os
import bcrypt
from app import create_app
from app.extensions import db
from app.models import User, Setting

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add default admin if not exists
        if not User.query.filter_by(username='admin').first():
            password = 'admin-password-123'
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(username='admin', password_hash=hashed)
            db.session.add(admin)
            print(f"Admin user created. Username: admin, Password: {password}")

        # Add default settings
        default_settings = {
            'phone': '+91 98765 43210',
            'address': '123 Spice Route Market, Foodie Lane, Downtown',
            'hours_weekday': '11:00 AM - 10:00 PM',
            'hours_saturday': '11:00 AM - 11:30 PM',
            'hours_sunday': '12:00 PM - 09:00 PM',
            'whatsapp_msg': 'Hello! I would like to order from The Food Palace.',
            'upi_id': 'yourname@upi',
            'banner_url': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDxdGJD02SEpQwhgK5tYawn0bqDEpEwA80r-MuTMhQKfCvhK3X81eOyHiZWeOILujV36ErDNr-iiJkwhUU9zn2uuv_eo34zJTCFeb-c0y-ANg3rKCuKe66LxHaBEpebMFdZWjTBDmEVpqtSde5hsINBnz5OdIKZGATXQmXXLJBtiy5kV7tZDgUQheIyQ0CydjjATjkqRQwTEcpFCtYfS054bEvUtoa4oHxg-g1LcjxLmed0EEUQRPXyfPq1MF0GFkOn3BbGkAoO_Ws'
        }

        for key, value in default_settings.items():
            if not Setting.query.filter_by(key=key).first():
                db.session.add(Setting(key=key, value=value))
        
        db.session.commit()
        print("The Food Palace Database initialized successfully.")

if __name__ == '__main__':
    init_db()
