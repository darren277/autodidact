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
import re


def parse_cornell_markdown(markdown_text: str):
    lines = markdown_text.splitlines()

    # Final structure
    data = {
        "date": "",
        "topic": "",
        "sections": []
    }

    current_section = None
    in_left_column = False
    in_right_column = False

    # We'll store the text that belongs to the current callout chunk here
    current_part = None

    # A small helper to decide the color category from the callout type
    def get_color_category(callout_type: str):
        if callout_type == "question":
            return "COLORS.QUESTION"
        elif callout_type == "note":
            return "COLORS.NOTE"
        else:
            return "COLORS.UNKNOWN"

    # Regex to parse the top-level date/topic line: # 2025-03-18 - Something
    title_line_re = re.compile(r"#\s+(\d{4}-\d{2}-\d{2})\s+-\s+(.*)")

    # Now iterate
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 1) Parse date/topic from first line starting w/ "# "
        if line.startswith("# "):
            m = title_line_re.match(line)
            if m:
                data["date"] = m.group(1)
                data["topic"] = m.group(2)
            i += 1
            continue

        # 2) Look for a new section
        if line.startswith("## "):
            # if there's an old section not appended, do so
            if current_section and current_section.get("parts"):
                data["sections"].append(current_section)

            # start a new section
            current_section = {
                "parts": [],
                "summary": ""
            }
            i += 1
            continue

        # 3) Check for multi-column toggles
        #    e.g. line.startswith("> [!multi-column]")
        if line.strip().startswith("> [!multi-column]"):
            # Toggle columns.
            # This depends on your exact logic for when to start left vs. right
            if not in_left_column and not in_right_column:
                # first time we see it in a section => left column
                in_left_column = True
                in_right_column = False
            else:
                # second time => switch to right column
                in_right_column = True
                in_left_column = False

            i += 1
            continue

        # 4) Look for a callout that starts with ">> [!something]"
        if line.strip().startswith(">> [!"):
            # if we were already capturing a part, push it into the section
            if current_part and current_section is not None:
                current_section["parts"].append(current_part)

            # parse the callout type: question, note, etc.
            # e.g. ">> [!question]" => question
            if line.strip().startswith(">> [!question]"):
                callout_type = "question"
            elif line.strip().startswith(">> [!note]"):
                callout_type = "note"
            else:
                callout_type = "unknown"

            # Initialize a new part
            current_part = {
                "category": get_color_category(callout_type),
                "lm": "",
                "main": ""
            }

            # If there is something like ">> [!question] **Date: 1967**"
            # you can parse out the text after [!question].
            # For simplicity let's just collect the entire line minus ">> [!question]"
            # but you can refine if you want to parse out bold text, etc.

            # remove leading >> [!question] portion
            # you might want a better pattern or to handle markdown better
            cleaned_line = re.sub(r">>\s*\[![a-zA-Z]+\]\s*", "", line.strip())
            cleaned_line = cleaned_line.strip()

            # We'll store that in "lm" if in_left_column else "rm"
            # but from your snippet you only show "lm" in final. You might want "rm" for the right column.
            # In your example JSON, you have "lm" in each part, so let's keep it simple:
            if in_left_column:
                current_part["lm"] = cleaned_line
            elif in_right_column:
                # If you truly want a separate field for the right column,
                # you might define "rm" or store it in the same "lm" field, up to you.
                current_part["lm"] = cleaned_line  # or something else
            else:
                # fallback if not sure
                current_part["lm"] = cleaned_line

            # Now we keep going on subsequent lines for “main” until next callout or summary
            i += 1
            # read lines until next ">> [!" or next "## " or next "> [!summary]" or next "[!multi-column]"...
            main_text_buffer = []
            while i < len(lines):
                nxt = lines[i]
                # stop conditions
                if nxt.strip().startswith(">> [!") or nxt.strip().startswith(
                        "> [!multi-column]") or nxt.strip().startswith("## ") or nxt.strip().startswith("# "):
                    # break so outer loop can handle it
                    break
                if nxt.strip().startswith("> [!summary]"):
                    # also break so summary can handle it
                    break
                # accumulate text
                main_text_buffer.append(nxt.lstrip("> "))  # remove leading > if present
                i += 1

            # assign the main text
            current_part["main"] = "\n".join(main_text_buffer).strip()
            continue

        # 5) Look for summary
        if line.strip().startswith("> [!summary]"):
            # read subsequent lines as summary
            summary_buffer = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                # break if we see a new callout or new multi-column or new section
                if nxt.strip().startswith(">> [!") or nxt.strip().startswith(
                        "> [!multi-column]") or nxt.strip().startswith("## ") or nxt.strip().startswith("# "):
                    break
                summary_buffer.append(nxt.lstrip("> "))
                i += 1

            if current_section is not None:
                current_section["summary"] = "\n".join(summary_buffer).strip()

            continue

        # if none of the above matched, just increment
        i += 1

    # if there's a leftover current_section with parts, append it
    if current_section and current_section.get("parts"):
        # if we were capturing a part not appended yet
        if current_part:
            current_section["parts"].append(current_part)
        data["sections"].append(current_section)

    return data


parsed = parse_cornell_markdown(s)
print(json.dumps(parsed, indent=2))



