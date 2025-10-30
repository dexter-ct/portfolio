from flask import Flask, render_template_string, request
import subprocess

app = Flask(__name__)

# Scripts
scripts = [
    {"label": "bulk_print", "path": r"[REDACTED_FILE_PATH]", "type": "python"},
    {"label": "service_charge", "path": r"[REDACTED_FILE_PATH]", "type": "python"},
    {"label": "allpay", "path": r"[REDACTED_FILE_PATH]", "type": "powershell"},
    {"label": "swipe_cards", "path": r"[REDACTED_FILE_PATH]", "type": "powershell"},
    {"label": "universal_credit", "path": r"[REDACTED_FILE_PATH]", "type": "powershell"},
    {"label": "split_pdf", "path": r"[REDACTED_FILE_PATH]", "type": "python"}
]

# Sleek dark grey UI
HTML_TEMPLATE = """
<!doctype html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>command_console</title>
    <style>
        body {
            background-color: #0a0a0a;
            color: #c0c0c0;
            font-family: 'Consolas', 'Courier New', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }

        .container {
            width: 600px;
            background-color: #111;
            border: 1px solid #222;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.4);
            padding: 30px 40px;
        }

        .title {
            text-align: left;
            font-size: 1.2rem;
            color: #888;
            text-transform: lowercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #222;
            padding-bottom: 10px;
            margin-bottom: 25px;
            opacity: 0.9;
        }

        .scripts {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: flex-start;
        }

        form {
            margin: 0;
        }

        button {
            background-color: #0f0f0f;
            color: #aaa;
            border: 1px solid #444;
            padding: 12px 20px;
            font-size: 14px;
            cursor: pointer;
            border-radius: 6px;
            font-family: 'Consolas', monospace;
            transition: all 0.2s ease-in-out;
            box-shadow: inset 0 0 6px rgba(255,255,255,0.05);
        }

        button:hover {
            background-color: #222;
            color: #ddd;
            border-color: #666;
            box-shadow: 0 0 8px rgba(255,255,255,0.1);
        }

        .message {
            margin-top: 25px;
            font-size: 14px;
            color: #bbb;
            text-align: left;
            background-color: #0d0d0d;
            border: 1px solid #222;
            border-radius: 6px;
            padding: 10px;
            white-space: pre-wrap;
            box-shadow: inset 0 0 8px rgba(255,255,255,0.05);
        }

        .message::before {
            content: "› ";
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">command_console</div>
        <div class="scripts">
            {% for script in scripts %}
                <form action="/run" method="post">
                    <input type="hidden" name="path" value="{{ script.path }}">
                    <input type="hidden" name="type" value="{{ script.type }}">
                    <button type="submit">{{ script.label }}</button>
                </form>
            {% endfor %}
        </div>
        {% if message %}
            <div class="message">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, scripts=scripts, message=None)

@app.route("/run", methods=["POST"])
def run_script():
    path = request.form['path']
    script_type = request.form['type']
    print(f"[INFO] Button clicked: {path} ({script_type})")
    message = ""
    try:
        if script_type == "python":
            result = subprocess.run(["python", path], capture_output=True, text=True)
        elif script_type == "powershell":
            result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", path], capture_output=True, text=True)
        else:
            raise ValueError(f"Unknown script type: {script_type}")

        message = f"{path} executed successfully.\n\n{result.stdout.strip() or 'No output'}"
    except Exception as e:
        message = f"Error running {path}: {str(e)}"

    return render_template_string(HTML_TEMPLATE, scripts=scripts, message=message)

if __name__ == "__main__":
    app.run(debug=True)