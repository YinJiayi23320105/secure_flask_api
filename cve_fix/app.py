from flask import Flask, request
from jinja2 import Template
app = Flask(__name__)
@app.route("/")
def index():
    name = request.args.get('name', 'guest')
    # Safe: Template source is static fixed string. User‑data passed as render‑time variable
    t = Template("Hello {{ name }}")
    return t.render(name=name)
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001)
