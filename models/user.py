""""""
# SQL-Alchemy User model with encrypted API key storage

from database import db
from datetime import datetime
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sub = db.Column(db.String(100), unique=True, nullable=False)  # Cognito sub
    encrypted_api_key = db.Column(db.Text, nullable=True)
    salt = db.Column(db.Text, nullable=True)  # Store as base64 string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"User('{self.email}', '{self.name}')"

    def json(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'sub': self.sub,
            'has_api_key': bool(self.encrypted_api_key),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_api_key(self, api_key, master_key):
        """Encrypt and store the API key"""
        if not api_key:
            self.encrypted_api_key = None
            self.salt = None
            return
        
        # Generate a salt for this user
        salt = os.urandom(16)
        
        # Derive a key from the master key and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        
        # Create Fernet cipher and encrypt the API key
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(api_key.encode())
        
        # Store the encrypted data as base64 string and salt as base64 string
        self.encrypted_api_key = base64.b64encode(encrypted_data).decode('utf-8')
        self.salt = base64.b64encode(salt).decode('utf-8')

    def get_api_key(self, master_key):
        """Decrypt and return the API key"""
        if not self.encrypted_api_key or not self.salt:
            return None
        
        try:
            # Decode the stored base64 strings back to bytes
            encrypted_data = base64.b64decode(self.encrypted_api_key.encode('utf-8'))
            salt = base64.b64decode(self.salt.encode('utf-8'))
            
            # Derive the key from the master key and salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            
            # Create Fernet cipher and decrypt the API key
            cipher = Fernet(key)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return decrypted_data.decode()
        except Exception as e:
            # If decryption fails, return None
            print(f"Failed to decrypt API key for user {self.id}: {e}")
            return None

    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_sub(cls, sub):
        """Find user by Cognito sub"""
        return cls.query.filter_by(sub=sub).first()

    @classmethod
    def create_or_update(cls, email, name, sub):
        """Create a new user or update existing one"""
        user = cls.find_by_sub(sub)
        if user:
            # Update existing user
            user.email = email
            user.name = name
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = cls(email=email, name=name, sub=sub)
            db.session.add(user)
        
        db.session.commit()
        return user 