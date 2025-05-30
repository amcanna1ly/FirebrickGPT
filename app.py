
from flask import Flask, request, render_template_string
from markupsafe import Markup
import subprocess
import shlex
import os
import re
from markdown import markdown

app = Flask(__name__)

def get_system_commands():
    result = subprocess.check_output(["bash", "-c", "compgen -c"], text=True)
    return set(result.strip().splitlines())

SYSTEM_COMMANDS = get_system_commands()

HTML = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>FirebrickGPT</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #1e1e1e;
      color: #eee;
      padding: 20px;
      transition: background-color 0.3s, color 0.3s;
    }
    .light-mode {
      background-color: #ffffff;
      color: #000000;
    }
    textarea {
      font-size: 16px;
    }
    .response-box {
      background: #2d2d2d;
      padding: 15px;
      border-radius: 8px;
      margin-top: 15px;
      white-space: pre-wrap;
      max-width: 1000px;
      margin-left: auto;
      margin-right: auto;
    }
    .light-mode .response-box {
      background: #f0f0f0;
      color: #000;
    }
    input[type=submit], .toggle-button {
      background-color: #007bff;
      border: none;
      color: white;
      padding: 10px 20px;
      font-size: 16px;
      border-radius: 5px;
      cursor: pointer;
    }
    input[type=submit]:hover, .toggle-button:hover {
      background-color: #0056b3;
    }
    footer {
      margin-top: 40px;
      text-align: center;
      font-size: 0.9em;
      opacity: 0.6;
    }
  </style>
</head>
<body>
  <button class="toggle-button" onclick="toggleTheme()">Toggle Dark/Light Mode</button>

  <div style="display: flex; justify-content: center;">
    <img src="/static/firebrickgpt_logo.png" alt="FirebrickGPT Logo" style="max-width: 300px; width: 100%%; height: auto; margin-bottom: 30px;">
  </div>

  <div style="display: flex; justify-content: center;">
    <form method="POST" style="width: 100%%; max-width: 1000px;">
      <textarea name="prompt" rows="8" style="width: 100%%;" placeholder="Type your question here..."></textarea><br><br>
      Max tokens to generate: <span id="tokenValue">{{ token_value }}</span><br>
      <input type="range" name="tokens" id="tokens" min="16" max="256" value="{{ token_value }}" step="16" oninput="tokenValue.innerText = this.value" style="width: 100%%;"><br><br>
      <label><input type="checkbox" name="command_mode" {% if command_mode %}checked{% endif %}> Enable Command Mode (Allow system actions)</label><br><br>
      <input type="submit" value="Submit">
    </form>
  </div>

  {% if response %}
    <h3 style="text-align:center;">Response</h3>
    <div class="response-box" id="response-box">{{ response|safe }}</div>
  {% endif %}

  <footer>
    &copy; 2025 FirebrickGPT - Built on a Raspberry Pi 5
  </footer>

  <script>
    function toggleTheme() {
      document.body.classList.toggle("light-mode");
    }

    const box = document.getElementById("response-box");
    if (box) {
      box.scrollIntoView({ behavior: "smooth" });
    }

    document.querySelector("textarea").addEventListener("keydown", function(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.form.submit();
      }
    });
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response = ''
    command_mode = False
    token_value = 64

    if request.method == "POST":
        prompt = request.form["prompt"]
        token_value = request.form.get("tokens", "64")
        command_mode = "command_mode" in request.form

        if command_mode:
            system_prompt = (
                "You are a helpful assistant. If the user asks for a system task, respond only with a valid Ubuntu shell command to perform that task. Do not explain or provide context."
            )
        else:
            system_prompt = (
                "You are a helpful assistant. Answer questions clearly and concisely. You may generate code, explain concepts, and provide complete answers. Do not include unrelated or extra information."
            )

        full_prompt = f"{system_prompt}\n\nQ: {prompt}\nA:"

        command = f"./llama/llama-cli -m ../models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf -p {shlex.quote(full_prompt)} -n {token_value} -t 4 --ctx-size 1024 --temp 0.7 --top-p 0.9 --repeat_penalty 1.1 --repeat_last_n 64 --mlock"

        try:
            raw_output = subprocess.check_output(command, shell=True, text=True)

            if command_mode:
                sanitized = re.sub(r"[`\\n\\r]", "", raw_output).strip()
                match = re.search(r"\b([a-zA-Z0-9_\-\.\/]+(?:\s[^|;&]*)?)", sanitized)

                if match:
                    shell_command = match.group(0).strip().split("|")[0].split()[0]
                    if shell_command in SYSTEM_COMMANDS:
                        try:
                            output = subprocess.check_output(sanitized, shell=True, text=True, stderr=subprocess.STDOUT)
                            response = f"```\n$ {sanitized}\n{output.strip()}\n```"
                        except subprocess.CalledProcessError as e:
                            response = f"```\n$ {sanitized}\nError:\n{e.output.strip()}\n```"
                    else:
                        response = f"Command `{shell_command}` is not allowed or not recognized."
                else:
                    response = "Unable to extract a valid system command from the model output."
            else:
                stripped_output = raw_output.replace(system_prompt.strip(), "").strip()
                stripped_output = stripped_output.replace("[end of text]", "").strip()
                response = Markup(markdown(stripped_output))

        except Exception as e:
            response = f"Error running model or command: {str(e)}"

    return render_template_string(HTML, response=response, command_mode=command_mode, token_value=token_value)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
