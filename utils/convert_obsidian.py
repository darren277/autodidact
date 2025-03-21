""""""

s = """
# 2025-03-18 - Cornell Notes Example

## Section 1

> [!multi-column]
>
>> [!question] **Date: 1967**
>> This is just a left column callout.
>
>> [!note] **Notes**
>> In 1967, the lorems discovered the ipsum. This was a groundbreaking discovery that changed how we understand the relationship between lorems and ipsums.

> [!multi-column]
>
>> [!question] **Idea: Lorem Ipsum**
>> Another left column callout.
>
>> [!note] **More Notes**
>> The lorems began cultivating ipsum in large quantities. This led to a period of great prosperity and advancement in lorem technologies throughout the late 1960s.

> [!summary]
> Lorem ipsum blah blah blah.

"""


import json


def parse_string(s: str):
    title_and_date = ""
    sections = []
    current_section_parts = []
    left_column = False
    right_column = False
    current_row = 0
    lines = s.split("\n")
    current_section = None
    for i, line in enumerate(lines):
        if line.startswith('# '):
            print("Found title and date")
            title_and_date = line[2:]
        elif line.startswith('## '):
            print("Found section")
            current_section = dict()
        elif line.startswith("> [!multi-column]"):
            print("Found multi-column")
            if left_column:
                left_column = False
                right_column = True
                current_row = 0
            else:
                left_column = True
                right_column = False
                current_row = 0
        elif line.startswith(">> [!"):
            if line.startswith(">> [!question]"): category = 'question'
            elif line.startswith(">> [!note]"): category = 'note'
            else: category = 'unknown'
            if left_column:
                current_section_parts[current_row]['lm'] = line + "\n" + lines[i+1]
            elif right_column:
                current_section_parts[current_row]['rm'] = line + "\n" + lines[i+1]
            current_section_parts[current_row]['category'] = category
        if line.startswith(">> [!summary]"):
            section_summary = line + "\n" + lines[i+1]
            current_section['summary'] = section_summary
            sections.append(current_section)
            current_section = dict()
            left_column = False
            right_column = False
            current_row = 0
            current_section_parts = []
        current_row += 1
    return title_and_date, sections


title_and_date, sections = parse_string(s)

print("Title and Date:", title_and_date)
print("Sections:", json.dumps(sections, indent=2))


