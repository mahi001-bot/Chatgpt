from flask import Flask, request, render_template_string, redirect, url_for, session
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY"

# -------- CONFIG --------
USERNAME = "DARKQUEEN"
PASSWORD = "DARKQUEEN"

# -------- STORAGE --------
inbox = {}

# -------- ROUTES --------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for("inbox_view"))
        return "❌ Invalid login"
    return """
    <form method="post">
      <input name="username" placeholder="Username"><br>
      <input name="password" type="password" placeholder="Password"><br>
      <button>Login</button>
    </form>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/inbox', methods=['GET','POST'])
def inbox_view():
    if not session.get('logged_in'):
        return redirect(url_for("login"))

    user = USERNAME

    # NP File Upload
    if request.method == "POST" and 'npFile' in request.files:
        f = request.files['npFile']
        if f and f.filename.endswith(".txt"):
            text = f.read().decode(errors="ignore")
            for line in text.splitlines():
                if line.strip():
                    inbox.setdefault(user, []).append({
                        "uid": uuid.uuid4().hex[:6],
                        "from": "np-file",
                        "text": line.strip(),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
        return redirect(url_for("inbox_view"))

    # Token File Upload
    if request.method == "POST" and 'tokenFile' in request.files:
        f = request.files['tokenFile']
        if f and f.filename:
            content = f.read().decode(errors="ignore")
            inbox.setdefault(user, []).append({
                "uid": uuid.uuid4().hex[:6],
                "from": "token-file",
                "text": f"Token file uploaded ({len(content)} chars)",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return redirect(url_for("inbox_view"))

    msgs = inbox.get(user, [])
    return render_template_string(INBOX_PAGE, msgs=msgs)


@app.route('/inbox/send', methods=['POST'])
def inbox_send():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    user = USERNAME
    text = request.form.get("text", "").strip()
    sender = request.form.get("from", "me")
    if text:
        inbox.setdefault(user, []).append({
            "uid": uuid.uuid4().hex[:6],
            "from": sender,
            "text": text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return redirect(url_for("inbox_view"))

@app.route('/inbox/clear')
def inbox_clear():
    if not session.get('logged_in'):
        return redirect(url_for("login"))
    inbox[USERNAME] = []
    return "cleared"

# -------- TEMPLATE --------
INBOX_PAGE = """<!doctype html><html><head>
  <title>Inbox Loader</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    #chatbox { max-height: 360px; overflow:auto; background:white; padding:12px; border-radius:6px; border:1px solid #eee;}
    .msg { margin-bottom:8px; }
  </style>
</head><body class="p-4">
  <a href="/logout" class="btn btn-sm btn-link">⬅ Logout</a>
  <div class="card p-3 mt-2">
    <h4>📥 Inbox Loader</h4>
    <div id="chatbox">
      {% for msg in msgs %}
        <div class="msg">
          <b>[UID: {{msg.uid}}]</b> <b>{{msg.from}}</b>: {{msg.text}}
          <small class="text-muted">({{msg.time}})</small>
        </div>
      {% else %}
        <div class="text-muted">No messages yet.</div>
      {% endfor %}
    </div>

    <!-- Send Form -->
    <form method="post" action="/inbox/send" class="mt-3 row g-2">
      <div class="col-md-3">
        <input name="from" class="form-control" placeholder="Hater's Name" required>
      </div>
      <div class="col-md-9 d-flex">
        <input name="text" class="form-control me-2" placeholder="Type a message..." required>
        <button class="btn btn-primary">Send</button>
      </div>
    </form>

    <!-- NP Text Upload -->
    <form method="post" enctype="multipart/form-data" class="mt-2">
      <label class="form-label">Upload NP Text File</label>
      <input type="file" name="npFile" accept=".txt" class="form-control mb-2">
      <button class="btn btn-sm btn-outline-dark">Upload NP File</button>
    </form>

    <!-- Token File Upload -->
    <form method="post" enctype="multipart/form-data" class="mt-2">
      <label class="form-label">Upload Token File</label>
      <input type="file" name="tokenFile" class="form-control mb-2">
      <button class="btn btn-sm btn-outline-dark">Upload Token</button>
    </form>

    <!-- Controls -->
    <div class="mt-3">
      <label>Speed (sec):</label>
      <input id="speedInput" type="number" value="5" min="1" class="form-control d-inline" style="width:80px;">
      <button id="runBtn" class="btn btn-sm btn-success">Run 🔥</button>
      <button id="stopBtn" class="btn btn-sm btn-warning">Stop ⏹</button>
      <button id="refreshBtn" class="btn btn-sm btn-outline-secondary">Refresh</button>
      <button id="clearBtn" class="btn btn-sm btn-outline-danger">Clear Inbox</button>
    </div>
  </div>

<script>
let autoRefresh = null;
document.getElementById("runBtn").onclick = () => {
  if(autoRefresh) return;
  let speed = parseInt(document.getElementById("speedInput").value) * 1000;
  autoRefresh = setInterval(()=>location.reload(), speed);
};
document.getElementById("stopBtn").onclick = () => {
  if(autoRefresh){ clearInterval(autoRefresh); autoRefresh=null; }
};
document.getElementById("refreshBtn").onclick = ()=>location.reload();
document.getElementById("clearBtn").onclick = ()=>{
  fetch('/inbox/clear').then(()=>location.reload());
};
</script>
</body></html>"""

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
