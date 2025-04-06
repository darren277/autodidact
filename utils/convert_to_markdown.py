""""""

'''
<article>
    <header>
        <div class="leftheader">Cues</div>
        <div class="rightheader">Date: {{ date }}. Topic: {{ topic }}.</div>
    </header>
    {% for s, section in enumerate(sections) %}
    <section>
        {% for i, part in enumerate(section.parts) %}
        <div class="leftmargin" id="leftmargin{{i}}">{{part.lm}}</div><div class="main" id="main{{i}}">{{part.main}}</div>
        {% endfor %}
        <footer>Summary: {{section.summary}}</footer>
    </section>
    {% endfor %}
</article>
'''


def convert_to_simple_markdown(data):
    markdown = f"# {data['topic']}\n\n"
    for section in data['sections']:
        for part in section['parts']:
            if 'title' in part:
                markdown += f"## {part['title']}\n\n"
            markdown += f"### {part['lm']}\n\n"
            markdown += f"{part['main']}\n\n"
    return markdown
