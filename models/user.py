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
    
    def get_lesson_progress(self, lesson_id):
        """Get progress for a specific lesson"""
        from models.lessons import UserProgress
        return UserProgress.query.filter_by(user_id=self.id, lesson_id=lesson_id).first()
    
    def get_or_create_lesson_progress(self, lesson_id):
        """Get existing progress for a lesson or create a new progress record"""
        from models.lessons import UserProgress
        return UserProgress.get_or_create(self.id, lesson_id)
    
    def mark_lesson_complete(self, lesson_id, percentage=100):
        """Mark a lesson as completed"""
        progress = self.get_or_create_lesson_progress(lesson_id)
        progress.mark_completed(percentage)
        return progress
    
    def update_lesson_progress(self, lesson_id, percentage, time_spent_minutes=None):
        """Update progress for a lesson"""
        progress = self.get_or_create_lesson_progress(lesson_id)
        progress.update_progress(percentage, time_spent_minutes)
        return progress
    
    def get_all_progress(self):
        """Get all progress records for this user"""
        return self.progress_records
    
    def get_completed_lessons(self):
        """Get all completed lessons"""
        return [p for p in self.progress_records if p.is_completed]
    
    def get_completion_stats(self):
        """Get overall completion statistics"""
        total_lessons = len(self.progress_records)
        completed_lessons = len(self.get_completed_lessons())
        
        if total_lessons == 0:
            return {
                'total_lessons': 0,
                'completed_lessons': 0,
                'completion_percentage': 0,
                'total_time_spent': 0
            }
        
        total_time_spent = sum(p.time_spent_minutes for p in self.progress_records)
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_percentage': int((completed_lessons / total_lessons) * 100),
            'total_time_spent': total_time_spent
        }
    
    def get_next_recommended_lesson(self):
        """Get the next recommended lesson for the user"""
        from models.lessons import UserProgress, Lesson
        
        # First, try to find an incomplete lesson that the user has started
        in_progress = UserProgress.query.filter_by(
            user_id=self.id
        ).filter(
            UserProgress.is_completed == False,
            UserProgress.percentage_completed > 0
        ).order_by(UserProgress.last_accessed.desc()).first()
        
        if in_progress:
            return in_progress.lesson
        
        # If no in-progress lessons, find the next unstarted lesson
        # Get all lesson IDs that the user has progress for
        user_lesson_ids = [p.lesson_id for p in self.progress_records]
        
        # Find the first lesson that the user hasn't started
        next_lesson = Lesson.query.filter(
            ~Lesson.id.in_(user_lesson_ids) if user_lesson_ids else True
        ).order_by(Lesson.id).first()
        
        return next_lesson
    
    def get_chat_history(self, lesson_id):
        """Get chat for a specific lesson"""
        from models.lessons import Chat
        return Chat.query.filter_by(user_id=self.id, lesson_id=lesson_id).first()
    
    def get_or_create_chat_history(self, lesson_id):
        """Get existing chat for a lesson or create a new one"""
        from models.lessons import Chat
        return Chat.get_or_create(self.id, lesson_id)
    
    def add_chat_message(self, lesson_id, message_type, content):
        """Add a message to the chat for a lesson"""
        chat = self.get_or_create_chat_history(lesson_id)
        message = chat.add_message(message_type, content)
        return chat
    
    def clear_chat_history(self, lesson_id):
        """Clear chat for a lesson"""
        chat = self.get_chat_history(lesson_id)
        if chat:
            chat.clear_messages()
        return chat
    
    def get_all_chat_histories(self):
        """Get all chats for this user"""
        return self.chats