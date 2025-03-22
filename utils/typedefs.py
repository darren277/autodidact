""""""
class StructuredNotesPart:
    def __init__(self, lm: str, main: str, category: Colors):
        self.lm = lm
        self.main = main
        self.category = category

    def serialize(self):
        return {
            "lm": self.lm,
            "main": self.main,
            "category": self.category
        }


class StructuredNotesSection:
    def __init__(self, *parts: StructuredNotesPart, summary: str):
        self.parts = parts
        self.summary = summary

    def serialize(self):
        return {
            "parts": [p.serialize() for p in self.parts],
            "summary": self.summary
        }


class StructuredNotes:
    def __init__(self, date: str, topic: str, *sections: StructuredNotesSection):
        self.date = date
        self.topic = topic
        self.sections = sections

    def serialize(self):
        return {
            "date": self.date,
            "topic": self.topic,
            "sections": [s.serialize() for s in self.sections]
        }
