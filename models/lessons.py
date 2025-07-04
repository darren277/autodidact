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
    
    # Additional fields for enhanced lesson display
    estimated_time_hours = db.Column(db.Integer, default=0)
    estimated_time_minutes = db.Column(db.Integer, default=30)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    tags = db.Column(db.Text)  # JSON string for tags
    learning_objectives = db.Column(db.Text)  # JSON string for learning objectives
    examples = db.Column(db.Text)  # Examples content
    exercises = db.Column(db.Text)  # Exercises content
    attachments = db.Column(db.Text)  # JSON string for attachments
    overview = db.Column(db.Text)  # Lesson overview/summary
    
    # Additional fields for lesson management
    featured_image = db.Column(db.String(500))  # URL to featured image
    published = db.Column(db.Boolean, default=False)  # Publication status
    order = db.Column(db.Integer, default=1)  # Order within module
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prerequisites = db.Column(db.Text)  # JSON string for prerequisite lesson IDs
    related_lessons = db.Column(db.Text)  # JSON string for related lesson IDs

    def __repr__(self):
        return f"Lesson('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'module_id': self.module_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'estimated_time_hours': self.estimated_time_hours,
            'estimated_time_minutes': self.estimated_time_minutes,
            'difficulty': self.difficulty,
            'tags': self.get_tags(),
            'learning_objectives': self.get_learning_objectives(),
            'examples': self.examples,
            'exercises': self.exercises,
            'attachments': self.get_attachments(),
            'overview': self.overview,
            'featured_image': self.featured_image,
            'published': self.published,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'prerequisites': self.get_prerequisites(),
            'related_lessons': self.get_related_lessons()
        }
    
    def get_tags(self):
        """Parse and return tags as list"""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except:
            return []
    
    def get_learning_objectives(self):
        """Parse and return learning objectives as list"""
        if not self.learning_objectives:
            return []
        try:
            import json
            return json.loads(self.learning_objectives)
        except:
            return []
    
    def get_attachments(self):
        """Parse and return attachments as list"""
        if not self.attachments:
            return []
        try:
            import json
            return json.loads(self.attachments)
        except:
            return []
    
    def get_prerequisites(self):
        """Parse and return prerequisites as list of lesson IDs"""
        if not self.prerequisites:
            return []
        try:
            import json
            return json.loads(self.prerequisites)
        except:
            return []
    
    def get_related_lessons(self):
        """Parse and return related lessons as list of lesson IDs"""
        if not self.related_lessons:
            return []
        try:
            import json
            return json.loads(self.related_lessons)
        except:
            return []


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    overview = db.Column(db.Text)
    resources = db.Column(db.Text)
    assessment = db.Column(db.Text)
    learning_outcomes = db.Column(db.Text)  # JSON string for learning outcomes
    featured_image = db.Column(db.String(500))  # URL to featured image
    attachments = db.Column(db.Text)  # JSON string for attachments
    prerequisites = db.Column(db.Text)  # JSON string for prerequisite module IDs
    related_modules = db.Column(db.Text)  # JSON string for related module IDs
    published = db.Column(db.Boolean, default=False)  # Publication status
    order = db.Column(db.Integer, default=1)  # Order within course
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    lessons = db.relationship('Lesson', backref='module', lazy=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __repr__(self):
        return f"Module('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'overview': self.overview,
            'resources': self.resources,
            'assessment': self.assessment,
            'learning_outcomes': self.get_learning_outcomes(),
            'featured_image': self.featured_image,
            'attachments': self.get_attachments(),
            'prerequisites': self.get_prerequisites(),
            'related_modules': self.get_related_modules(),
            'published': self.published,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'lessons': [lesson.json() for lesson in self.lessons],
            'course_id': self.course_id
        }
    
    def get_learning_outcomes(self):
        """Parse and return learning outcomes as list"""
        if not self.learning_outcomes:
            return []
        try:
            import json
            return json.loads(self.learning_outcomes)
        except:
            return []
    
    def get_attachments(self):
        """Parse and return attachments as list"""
        if not self.attachments:
            return []
        try:
            import json
            return json.loads(self.attachments)
        except:
            return []
    
    def get_prerequisites(self):
        """Parse and return prerequisites as list of module IDs"""
        if not self.prerequisites:
            return []
        try:
            import json
            return json.loads(self.prerequisites)
        except:
            return []
    
    def get_related_modules(self):
        """Parse and return related modules as list of module IDs"""
        if not self.related_modules:
            return []
        try:
            import json
            return json.loads(self.related_modules)
        except:
            return []


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    overview = db.Column(db.Text)
    objectives = db.Column(db.Text)  # JSON string for course objectives
    prerequisites = db.Column(db.Text)  # JSON string for course prerequisites
    featured_image = db.Column(db.String(500))  # URL to featured image
    attachments = db.Column(db.Text)  # JSON string for attachments
    published = db.Column(db.Boolean, default=False)  # Publication status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    modules = db.relationship('Module', backref='course', lazy=True)

    def __repr__(self):
        return f"Course('{self.title}')"

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'overview': self.overview,
            'objectives': self.get_objectives(),
            'prerequisites': self.get_prerequisites(),
            'featured_image': self.featured_image,
            'attachments': self.get_attachments(),
            'published': self.published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'modules': [module.json() for module in self.modules]
        }
    
    def get_objectives(self):
        """Parse and return objectives as list"""
        if not self.objectives:
            return []
        try:
            import json
            return json.loads(self.objectives)
        except:
            return []
    
    def get_prerequisites(self):
        """Parse and return prerequisites as list"""
        if not self.prerequisites:
            return []
        try:
            import json
            return json.loads(self.prerequisites)
        except:
            return []
    
    def get_attachments(self):
        """Parse and return attachments as list"""
        if not self.attachments:
            return []
        try:
            import json
            return json.loads(self.attachments)
        except:
            return []


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


class UserProgress(db.Model):
    # Tracks user progress on individual lessons
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    
    # Progress tracking fields
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    percentage_completed = db.Column(db.Integer, default=0)  # 0-100
    time_spent_minutes = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='progress_records')
    lesson = db.relationship('Lesson', backref='user_progress')
    
    # Unique constraint to ensure one progress record per user per lesson
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_progress_uc'),)

    def __repr__(self):
        return f"UserProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.is_completed})"

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'is_completed': self.is_completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'percentage_completed': self.percentage_completed,
            'time_spent_minutes': self.time_spent_minutes,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_or_create(cls, user_id, lesson_id):
        """Get existing progress record or create a new one"""
        progress = cls.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        if not progress:
            progress = cls(user_id=user_id, lesson_id=lesson_id)
            db.session.add(progress)
            db.session.commit()
        return progress
    
    def mark_completed(self, percentage=100):
        """Mark the lesson as completed"""
        self.is_completed = True
        self.percentage_completed = percentage
        self.completion_date = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def update_progress(self, percentage, time_spent_minutes=None):
        """Update progress percentage and optionally time spent"""
        self.percentage_completed = max(0, min(100, percentage))  # Ensure 0-100 range
        self.last_accessed = datetime.utcnow()
        
        if time_spent_minutes is not None:
            self.time_spent_minutes = time_spent_minutes
        
        # Auto-mark as completed if percentage reaches 100
        if self.percentage_completed >= 100:
            self.is_completed = True
            self.completion_date = datetime.utcnow()
        
        db.session.commit()

