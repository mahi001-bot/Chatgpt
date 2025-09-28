from flask import Flask, request, render_template_string, redirect, session, url_for, jsonify
import threading, time, uuid, random, requests
from datetime import datetime

# ✅ Flask app with correct name init
app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET"

# ✅ Login credentials
USERNAME = "MahiX"
PASSWORD = "MahiX"

# ✅ Jobs and shared lists
jobs = {}

tokens_list = []
uids_list = []
comments_list = []

global_settings = {"delay": 10}

# ✅ Template renamed to D49D M9HI
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 D49D M9HI AUTO SERVER</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background:#000; color:#0ff; font-family:monospace; }
        .log-box { background:#111; border-radius:10px; padding:10px; max-height:300px; overflow-y:auto; }
        .btn-danger { background-color:#f00; border:none; }
        .btn-success { background-color:#0f0; color:#000; border:none; }
        .btn-warning { background-color:#ff0; color:#000; border:none; }
        .job-card { background:#111; padding:5px; border-radius:8px; margin-bottom:5px; }
    </style>
</head>
<body class="container py-4">
    <h2 class="text-center">🚀 D49D M9HI AUTO SERVER</h2>

    <form method="POST" action="/upload_tokens" enctype="multipart/form-data" class="mb-3">
        <label>🔑 Upload Tokens File</label>
        <input type="file" name="file" class="form-control mb-2" required>
        <button class="btn btn-warning w-100">📤 Upload Tokens</button>
    </form>

    <form method="POST" action="/upload_uids" enctype="multipart/form-data" class="mb-3">
        <label>🆔 Upload UIDs File</label>
        <input type="file" name="file" class="form-control mb-2" required>
        <button class="btn btn-warning w-100">📤 Upload UIDs</button>
    </form>

    <form method="POST" action="/upload_comments" enctype="multipart/form-data" class="mb-3">
        <label>📄 Upload Comments File</label>
        <input type="file" name="file" class="form-control mb-2" required>
        <button class="btn btn-warning w-100">📤 Upload Comments</button>
    </form>

    <form method="POST" action="/set_delay" class="mb-3">
        <label>⏱ Set Delay (Seconds)</label>
        <input type="number" name="delay" class="form-control mb-2" value="10" min="1">
        <button class="btn btn-warning w-100">💾 Save Delay</button>
    </form>

    <form method="POST" action="/start" class="mb-2">
        <button class="btn btn-danger w-100">🚀 Start New Job</button>
    </form>

    <h4>📜 Active Jobs</h4>
    <div id="jobs"></div>

    <h4>📜 Logs</h4>
    <div class="log-box" id="logs"></div>

<script>
async function fetchData(){
    const res = await fetch('/jobs');
    const data = await res.json();
    document.getElementById('logs').innerText = data.logs.join("\\n");
    const jobsDiv = document.getElementById('jobs');
    jobsDiv.innerHTML = "";
    data.active_jobs.forEach(job => {
        jobsDiv.innerHTML += `
            <div class="job-card">
                <b>🆔 Job:</b> ${job.id} | <b>Status:</b> ${job.running ? "✅ Running" : "🛑 Stopped"}
                <form method="POST" action="/stop/${job.id}">
                    <button class="btn btn-success btn-sm mt-1 w-100">Stop This Job</button>
                </form>
            </div>`;
    });
}
setInterval(fetchData, 3000);
fetchData();
</script>
</body>
</html>
"""

# ✅ Function placeholder (still posts but you can replace)
def post_on_uid_wall(token, uid, message):
    try:
        url = f"https://graph.facebook.com/{uid}/feed"
        r = requests.post(url, data={"message": message, "access_token": token})
        return r.status_code, r.text
    except Exception as e:
        return 500, str(e)

# ✅ Worker thread
def run_job(job_id):
    while jobs[job_id]["running"]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not comments_list:
            jobs[job_id]["logs"].append(f"[{now}] ❌ No comments found! Skipping.")
            time.sleep(global_settings["delay"])
            continue

        if not tokens_list or not uids_list:
            jobs[job_id]["logs"].append(f"[{now}] ❌ Tokens or UIDs missing! Stopping job.")
            break

        message = random.choice(comments_list)
        token = random.choice(tokens_list)
        uid = random.choice(uids_list)

        status, _ = post_on_uid_wall(token, uid, message)
        jobs[job_id]["logs"].append(f"[{now}] ✅ UID {uid} -> {status}")
        time.sleep(global_settings["delay"])

# ✅ Routes
@app.route("/", methods=["GET"])
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template_string(TEMPLATE)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == USERNAME and request.form.get("password") == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        return "<h3 style='color:red;'>❌ Wrong Username/Password</h3>"
    return "<h3>Login Page</h3>"

@app.route("/upload_tokens", methods=["POST"])
def upload_tokens():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if "file" in request.files:
        data = request.files["file"].read().decode("utf-8")
        tokens_list.clear()
        tokens_list.extend([t.strip() for t in data.splitlines() if t.strip()])
    return redirect(url_for("home"))

@app.route("/upload_uids", methods=["POST"])
def upload_uids():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if "file" in request.files:
        data = request.files["file"].read().decode("utf-8")
        uids_list.clear()
        uids_list.extend([u.strip() for u in data.splitlines() if u.strip()])
    return redirect(url_for("home"))

@app.route("/upload_comments", methods=["POST"])
def upload_comments():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if "file" in request.files:
        data = request.files["file"].read().decode("utf-8")
        comments_list.clear()
        comments_list.extend([c.strip() for c in data.splitlines() if c.strip()])
    return redirect(url_for("home"))

@app.route("/set_delay", methods=["POST"])
def set_delay():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    delay = request.form.get("delay", type=int)
    if delay and delay > 0:
        global_settings["delay"] = delay
    return redirect(url_for("home"))

@app.route("/start", methods=["POST"])
def start_job():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    job_id = str(uuid.uuid4())[:6]
    jobs[job_id] = {"running": True, "logs": []}
    threading.Thread(target=run_job, args=(job_id,), daemon=True).start()
    return redirect(url_for("home"))

@app.route("/stop/<job_id>", methods=["POST"])
def stop_job(job_id):
    if job_id in jobs:
        jobs[job_id]["running"] = False
        jobs.pop(job_id, None)
    return redirect(url_for("home"))

@app.route("/jobs")
def list_jobs():
    data = {"logs": [], "active_jobs": []}
    for jid, info in jobs.items():
        data["logs"] += info["logs"][-20:]
        data["active_jobs"].append({"id": jid, "running": info["running"]})
    return jsonify(data)

# ✅ Correct main entry
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
