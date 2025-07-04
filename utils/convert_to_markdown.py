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
    # Handle simple content (just a string or dict with content)
    if isinstance(data, str):
        return data
    
    if isinstance(data, dict) and 'content' in data:
        return data['content']
    
    # Handle structured data (with topic, sections, parts)
    if isinstance(data, dict) and 'topic' in data and 'sections' in data:
        markdown = f"# {data['topic']}\n\n"
        for section in data.get('sections', []):
            for part in section.get('parts', []):
                if 'title' in part:
                    markdown += f"## {part['title']}\n\n"
                if 'lm' in part:
                    markdown += f"### {part['lm']}\n\n"
                if 'main' in part:
                    markdown += f"{part['main']}\n\n"
        return markdown
    
    # Fallback: return the data as string
    return str(data)
