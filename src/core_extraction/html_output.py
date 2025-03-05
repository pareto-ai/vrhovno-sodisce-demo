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
                styled_text.append(f'<span style="color: green"><b>{segment}</b></span>')
            elif is_red:
                styled_text.append(f'<span style="color: blue;"><b>{segment}</b></span>')
            elif is_underlined:
                styled_text.append(f'<span style="color: red"><b>{segment}</b></span>')
            else:
                styled_text.append(segment)

        last_idx = idx
    styled_text.append(text[last_idx:])

    return ''.join(styled_text)


def save_html_to_file(main_text, right_texts, filename="output.html"):
    """
    Saves structured HTML with two columns:
    - Left column: Main text
    - Right column: Three distinct text blocks

    Parameters:
        main_text (str): The main body text (left column).
        right_texts (list of str): Three texts for the right column.
        filename (str): Name of the output file.
    """

    # Define a CSS style for proper layout
    css_styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1500px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f4f4f4;
        }
        .container {
            display: flex;
            gap: 20px;
        }
        .left-column {
            flex: 1.2;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .right-column {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .right-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
    """

    # Wrap the content in a full HTML structure
    full_html = f"""
    <html>
    <head>
        <title>Styled Layout</title>
        {css_styles}
    </head>
    <body>
        <div class="container">
            <div class="left-column">
                <p>{main_text}</p>
            </div>
            <div class="right-column">
                <div class="right-box"><p>{right_texts[0]}</p></div>
                <div class="right-box"><p>{right_texts[1]}</p></div>
                <div class="right-box"><p>{right_texts[2]}</p></div>
            </div>
        </div>
    </body>
    </html>
    """

    # Use BeautifulSoup to prettify the HTML
    soup = BeautifulSoup(full_html, "html.parser")

    # Write the formatted HTML to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print(f"HTML saved successfully to {filename}")





