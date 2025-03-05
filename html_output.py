from bs4 import BeautifulSoup

def apply_styles(text, red_spans, underline_spans):
    # Identify all unique indices to split the text
    indices = set()
    for start, end in red_spans + underline_spans:
        indices.add(start)
        indices.add(end)

    indices = sorted(indices)

    # Create segments with styles
    styled_text = []
    last_idx = 0

    for idx in indices:
        if last_idx != idx:
            segment = text[last_idx:idx]
            is_red = any(start <= last_idx < end for start, end in red_spans)
            is_underlined = any(start <= last_idx < end for start, end in underline_spans)

            # Apply styles
            if is_red and is_underlined:
                styled_text.append(f'<span style="color: red; text-decoration: underline;">{segment}</span>')
            elif is_red:
                styled_text.append(f'<span style="color: red;">{segment}</span>')
            elif is_underlined:
                styled_text.append(f'<span style="text-decoration: underline;">{segment}</span>')
            else:
                styled_text.append(segment)

        last_idx = idx
    styled_text.append(text[last_idx:])

    return ''.join(styled_text)


def save_html_to_file(html_content, filename="output.html"):
    # Define a CSS style for better readability
    css_styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f4f4f4;
        }
        p {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        span {
            font-weight: bold;
        }
    </style>
    """

    # Wrap the content in a full HTML structure
    full_html = f"""
    <html>
    <head>
        <title>Styled Text</title>
        {css_styles}
    </head>
    <body>
        <p>{html_content}</p>
    </body>
    </html>
    """

    # Use BeautifulSoup to prettify the HTML
    soup = BeautifulSoup(full_html, "html.parser")

    # Write the formatted HTML to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print(f"HTML saved successfully to {filename}")







