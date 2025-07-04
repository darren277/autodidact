""""""
# SQL-Alchemy models for Lessons and Modules and Courses.
# One Course consists of Many Modules.
# One Module consists of Many Lessons.

from database import db
from datetime import datetime

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))

    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    # TODO: attachments = db.Column(db.Text)

    def __repr__(self):
        return f"Lesson('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'module_id': self.module_id,
            'start_date': self.start_date,
            'end_date': self.end_date
            # TODO: 'attachments': self.attachments
        }


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    lessons = db.relationship('Lesson', backref='module', lazy=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __repr__(self):
        return f"Module('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'lessons': [lesson.json() for lesson in self.lessons],
            'course_id': self.course_id
        }


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    modules = db.relationship('Module', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'modules': [module.json() for module in self.modules]
        }


class Notes(db.Model):
    # Notes have a one to one relationship with a lesson and user
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Additional fields for structured notes
    note_type = db.Column(db.String(50), default='text')  # 'text', 'cornell', 'mindmap', etc.
    structured_data = db.Column(db.Text)  # JSON string for structured notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Notes('{self.content}')"

    def json(self):
        return {
            'id': self.id,
            'content': self.content,
            'lesson_id': self.lesson_id,
            'user_id': self.user_id,
            'note_type': self.note_type,
            'structured_data': self.structured_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_structured_data(self):
        """Parse and return structured data as dict"""
        if not self.structured_data:
            return None
        try:
            import json
            return json.loads(self.structured_data)
        except:
            return None


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(50))  # 'video', 'audio', 'image'
    annotations = db.Column(db.Text)  # JSON string for annotations
    segments = db.Column(db.Text)  # JSON string for segments
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Media('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'annotations': self.get_annotations(),
            'segments': self.get_segments(),
            'lesson_id': self.lesson_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_annotations(self):
        """Parse and return annotations as list"""
        if not self.annotations:
            return []
        try:
            import json
            return json.loads(self.annotations)
        except:
            return []
    
    def get_segments(self):
        """Parse and return segments as list"""
        if not self.segments:
            return []
        try:
            import json
            return json.loads(self.segments)
        except:
            return []


class Quiz(db.Model):
    # Quizzes have a one to one relationship with a lesson
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))

    def __repr__(self):
        return f"Quiz('{self.content}')"

    def json(self):
        return {
            'id': self.id,
            'content': self.content,
            'lesson_id': self.lesson_id
        }

