import re
from markupsafe import Markup, escape


def markdown_to_html(text):
    """A minimal markdown-to-HTML converter for blog post content."""
    if not text:
        return ""
    lines = text.split("\n")
    html = []
    in_list = False
    in_code = False
    code_block = []

    for line in lines:
        # Code block
        if line.strip().startswith("```"):
            if in_code:
                html.append("<pre><code>" + escape("\n".join(code_block)) + "</code></pre>")
                code_block = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_block.append(line)
            continue

        # Headings
        if line.startswith("# "):
            html.append("<h2>" + escape(line[2:]) + "</h2>")
            continue
        elif line.startswith("## "):
            html.append("<h3>" + escape(line[3:]) + "</h3>")
            continue
        elif line.startswith("### "):
            html.append("<h4>" + escape(line[4:]) + "</h4>")
            continue

        # Unordered list
        if re.match(r"^\s*[-*]\s", line):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append("<li>" + inline_format(re.sub(r"^\s*[-*]\s", "", line)) + "</li>")
            continue
        else:
            if in_list:
                html.append("</ul>")
                in_list = False

        # Horizontal rule
        if re.match(r"^\s*(---|\*\*\*)\s*$", line):
            html.append("<hr>")
            continue

        # Blank line
        if not line.strip():
            html.append("")
            continue

        # Paragraph
        html.append("<p>" + inline_format(line) + "</p>")

    if in_list:
        html.append("</ul>")
    if in_code:
        html.append("<pre><code>" + escape("\n".join(code_block)) + "</code></pre>")

    return "\n".join(html)


def inline_format(text):
    """Apply inline formatting: bold, italic, links, inline code."""
    text = escape(text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_filter(text):
    return Markup(markdown_to_html(text))
