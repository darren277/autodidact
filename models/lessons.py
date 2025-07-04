""""""
# SQL-Alchemy models for Lessons and Modules and Courses.
# One Course consists of Many Modules.
# One Module consists of Many Lessons.

from database import db

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

    def __repr__(self):
        return f"Notes('{self.content}')"

    def json(self):
        return {
            'id': self.id,
            'content': self.content,
            'lesson_id': self.lesson_id,
            'user_id': self.user_id
        }


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

