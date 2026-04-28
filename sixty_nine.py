from flask import Flask
import random

app = Flask(__name__)

FONTS = [
    ("Bebas Neue",        "https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap"),
    ("Oswald",            "https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap"),
    ("Russo One",         "https://fonts.googleapis.com/css2?family=Russo+One&display=swap"),
    ("Anton",             "https://fonts.googleapis.com/css2?family=Anton&display=swap"),
    ("Black Ops One",     "https://fonts.googleapis.com/css2?family=Black+Ops+One&display=swap"),
    ("Permanent Marker",  "https://fonts.googleapis.com/css2?family=Permanent+Marker&display=swap"),
    ("Lobster",           "https://fonts.googleapis.com/css2?family=Lobster&display=swap"),
    ("Pacifico",          "https://fonts.googleapis.com/css2?family=Pacifico&display=swap"),
    ("Righteous",         "https://fonts.googleapis.com/css2?family=Righteous&display=swap"),
    ("Fredoka One",       "https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap"),
    ("Monoton",           "https://fonts.googleapis.com/css2?family=Monoton&display=swap"),
    ("Bungee",            "https://fonts.googleapis.com/css2?family=Bungee&display=swap"),
    ("Press Start 2P",    "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"),
    ("Titan One",         "https://fonts.googleapis.com/css2?family=Titan+One&display=swap"),
    ("Alfa Slab One",     "https://fonts.googleapis.com/css2?family=Alfa+Slab+One&display=swap"),
]

GRADIENTS = [
    "linear-gradient(135deg, #ff6b6b, #ffd93d)",
    "linear-gradient(135deg, #6bcb77, #4d96ff)",
    "linear-gradient(135deg, #f72585, #7209b7)",
    "linear-gradient(135deg, #ff9a00, #ff0058)",
    "linear-gradient(135deg, #00f5d4, #00bbf9)",
    "linear-gradient(135deg, #ffffff, #888888)",
    "linear-gradient(135deg, #f9c74f, #f8961e)",
    "linear-gradient(135deg, #43aa8b, #577590)",
]


@app.route("/")
def index():
    font_name, font_url = random.choice(FONTS)
    gradient = random.choice(GRADIENTS)
    bg_color = "#" + "%06x" % random.randint(0x0a0a0a, 0x1a1a2e)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>69</title>
    <link href="{font_url}" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: {bg_color};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }}

        .number {{
            font-family: '{font_name}', Impact, sans-serif;
            font-size: 38vw;
            line-height: 0.85;
            width: 100vw;
            text-align: center;
            background: {gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            user-select: none;
        }}

        .label {{
            margin-top: 2rem;
            font-family: monospace;
            font-size: 0.9rem;
            color: #444;
            letter-spacing: 0.3em;
            text-transform: uppercase;
        }}

        .label span {{
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="number">69</div>
    <div class="label"><span>font:</span> {font_name} &nbsp;&mdash;&nbsp; <span>reload for next</span></div>
</body>
</html>"""
    return html


if __name__ == "__main__":
    app.run(debug=True, port=5001)
