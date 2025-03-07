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
    - Left column: Main text with header and legend
    - Right column: Three distinct text blocks with headers

    Parameters:
        main_text (str): The main body text (left column).
        right_texts (list of str): Three texts for the right column.
        filename (str): Name of the output file.
    """

    # Define CSS styles for layout and colors
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
            display: flex;
            flex-direction: column;
            justify-content: space-between;
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
        .left-box {
            background: white;
            padding: 5px;
        }
        .box-header {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
        }
        .legend {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            font-weight: bold;
        }
        .legend span {
            padding: 5px 10px;
            border-radius: 5px;
        }
        .blue { color: blue; }
        .red { color: red; }
        .green { color: green; }
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
                <div class="left-box">
                    <div class="box-header">Obrazložitev</div>
                    <p>{main_text}</p>
                </div>
                <div class="legend">
                    <span class="blue">AI</span>
                    <span class="red">Človek</span>
                    <span class="green">Oba</span>
                </div>
            </div>
            <div class="right-column">
                <div class="right-box"><div class="box-header">AI jedro</div><p>{right_texts[0]}</p></div>
                <div class="right-box"><div class="box-header">Pravo jedro</div><p>{right_texts[1]}</p></div>
                <div class="right-box"><div class="box-header">Metrike</div><p>{right_texts[2]}</p></div>
                <div class="right-box"><div class="box-header">Zveza</div><p>{right_texts[3]}</p></div>
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





