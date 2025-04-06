""""""
example_lesson = {"id": 1, "title": "Lesson 1", "content": "This is the content for Lesson 1."}

example_lesson.update(
    estimated_time=dict(
        hours=1,
        minutes=30
    ),
    difficulty="Intermediate",
    tags=["Python", "Programming", "Web Development"]
)

example_lesson.update(topic="Python Programming")

example_lesson.update(user_progress=dict(completed=True))
