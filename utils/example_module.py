""""""

example_module_progress = {
    "completed": 2,
    "total": 5,
    "percentage": 40
}

example_module_lesson_cards = [
    {
        "id": "1",
        "status": "completed",
        "icon": "✓",
        "title": "1. Introduction to Lorem Ipsum",
        "description": "Learn the basic principles and history of Lorem Ipsum.",
        "duration": "15 min",
        "action": "Review"
    },
    {
        "id": "2",
        "status": "completed",
        "icon": "✓",
        "title": "2. Dolor Sit Amet Techniques",
        "description": "Explore various techniques used in Dolor Sit Amet methodology.",
        "duration": "20 min",
        "action": "Review"
    },
    {
        "id": "3",
        "status": "current",
        "icon": "•",
        "title": "3. Practical Applications",
        "description": "Apply your knowledge to real-world scenarios and case studies.",
        "duration": "25 min",
        "action": "Continue"
    },
    {
        "id": "4",
        "status": "",
        "icon": "",
        "title": "4. Advanced Concepts",
        "description": "Dive deeper into complex aspects of Lorem Ipsum Dolor.",
        "duration": "30 min",
        "action": "Start"
    },
    {
        "id": "5",
        "status": "",
        "icon": "",
        "title": "5. Review & Assessment",
        "description": "Consolidate your learning and test your knowledge.",
        "duration": "20 min",
        "action": "Start"
    },
    {
        "id": "6",
        "status": "completed",
        "icon": "✓",
        "title": "6. Final Exam",
        "description": "Test your knowledge with a comprehensive exam.",
        "duration": "1 hour",
        "action": "Review"
    }
]

example_module_resources = [
    {
        "icon": "📄",
        "title": "Lorem Ipsum: A Comprehensive Guide",
        "description": "A detailed reference document covering all aspects of Lorem Ipsum",
        "link": "#",
        "action": "View"
    },
    {
        "icon": "🎥",
        "title": "Video Tutorial: Dolor Sit Amet in Practice",
        "description": "Watch an expert demonstrate key techniques",
        "link": "/annotated_media/1",
        "action": "Watch"
    },
    {
        "icon": "🔗",
        "title": "External Reading: History of Lorem Ipsum",
        "description": "An in-depth article on the origins and evolution of Lorem Ipsum",
        "link": "#",
        "action": "Visit"
    }
]

example_module = dict(
    title="Module 1: Introduction to Lorem Ipsum",
    page_title="Module 1: Introduction to Lorem Ipsum",
    module_progress=example_module_progress,
    module_download_materials_link="#",
    module_take_quiz_link="#",
    module_description="""
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam varius massa vitae semper consectetur. Proin lobortis, nunc nec vehicula posuere, turpis velit scelerisque nisi, et convallis lectus massa eget eros.</p>
    <p>This module will cover fundamental concepts of Lorem Ipsum and provide practical exercises to reinforce your understanding.</p>
    """,
    lesson_cards=example_module_lesson_cards,
    resources=example_module_resources
)