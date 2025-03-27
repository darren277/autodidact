""""""
# SQL-Alchemy models for Lessons and Modules
# One Module consists of Many Lessons.

from main import db

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))

    def __repr__(self):
        return f"Lesson('{self.title}')"


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    lessons = db.relationship('Lesson', backref='module', lazy=True)

    def __repr__(self):
        return f"Module('{self.title}')"


class Notes(db.Model):
    # Notes have a one to one relationship with a lesson
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))

    def __repr__(self):
        return f"Notes('{self.content}')"


class Quiz(db.Model):
    # Quizzes have a one to one relationship with a lesson
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))

    def __repr__(self):
        return f"Quiz('{self.content}')"

