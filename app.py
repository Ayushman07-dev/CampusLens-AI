import os, sqlite3
from datetime import datetime, timezone
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "campuslens-dev-key")
DB_PATH = os.getenv("DATABASE_PATH", "/tmp/campuslens.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT NOT NULL, location TEXT NOT NULL,
            category TEXT NOT NULL, urgency INTEGER NOT NULL, accessibility INTEGER NOT NULL,
            disruption INTEGER NOT NULL, recurrence INTEGER NOT NULL, priority INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Submitted', created_at TEXT NOT NULL
        )""")
init_db()

PAGE = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CampusLens AI — Campus Issue Reporting</title>
<style>
:root{--ink:#17243b;--muted:#66758c;--blue:#315ce8;--bg:#f4f7fc;--line:#e3e9f3}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Arial,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:22px max(22px,calc((100% - 1080px)/2));background:#fff;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}
.brand{font-size:21px;font-weight:800;letter-spacing:-.5px}.brand span{color:var(--blue)}header a{color:var(--blue);text-decoration:none;font-weight:650}
main{max-width:1080px;margin:42px auto;padding:0 20px}.hero{padding:38px;border-radius:24px;background:linear-gradient(120deg,#172b54,#315ce8);color:white}
.eyebrow{text-transform:uppercase;letter-spacing:2px;font-size:12px;font-weight:800;opacity:.8}.hero h1{font-size:clamp(30px,5vw,48px);line-height:1.1;max-width:680px;margin:14px 0}.hero p{max-width:640px;line-height:1.7;color:#e4ebff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:22px}.card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:24px;box-shadow:0 10px 30px #23365a08}.card h2{margin-top:0;font-size:21px}
label{display:block;font-size:13px;font-weight:700;margin:14px 0 7px}input,textarea,select{width:100%;padding:12px;border:1px solid #d4ddeb;border-radius:10px;font:inherit;background:#fff}textarea{min-height:95px;resize:vertical}.scores{display:grid;grid-template-columns:1fr 1fr;gap:12px}
button{margin-top:18px;background:var(--blue);color:#fff;border:0;padding:13px 18px;border-radius:11px;font-weight:750;cursor:pointer;width:100%}.notice{padding:12px 14px;background:#e9f8ef;color:#17653b;border-radius:10px;margin:16px 0}.muted{color:var(--muted);font-size:14px;line-height:1.6}.pill{background:#edf2ff;color:#315ce8;border-radius:30px;padding:5px 9px;font-size:12px;font-weight:750}.report{padding:14px 0;border-bottom:1px solid var(--line)}.report:last-child{border:0}.report strong{display:block;margin-bottom:5px}.footer{text-align:center;color:var(--muted);padding:30px;font-size:13px}
@media(max-width:760px){.grid{grid-template-columns:1fr}.hero{padding:26px}main{margin-top:24px}header{padding:18px 20px}}
</style></head><body><header><div class="brand">CampusLens <span>AI</span></div><a href="#report">Report an issue ↗</a></header>
<main><section class="hero"><div class="eyebrow">A better campus starts with being heard</div><h1>See an issue? Help make campus better.</h1><p>Report accessibility barriers, maintenance problems, sanitation concerns, or safety issues. CampusLens helps organize reports using a transparent priority score so campus teams can review what needs attention first.</p></section>
{% with messages = get_flashed_messages() %}{% if messages %}<div class="notice">{{ messages[0] }}</div>{% endif %}{% endwith %}
<div class="grid"><section class="card" id="report"><h2>Submit a campus report</h2><p class="muted">Share clear details so the right team can review your concern.</p>
<form method="post" action="/report"><label for="title">Issue title</label><input id="title" name="title" required maxlength="120" placeholder="e.g. Ramp blocked near library">
<label for="description">Description</label><textarea id="description" name="description" required maxlength="2000" placeholder="What happened and who is affected?"></textarea>
<label for="location">Campus location</label><input id="location" name="location" required maxlength="160" placeholder="Building, floor, or nearby landmark">
<label for="category">Category</label><select id="category" name="category"><option>Accessibility</option><option>Maintenance</option><option>Sanitation</option><option>Safety</option><option>Other</option></select>
<div class="scores"><div><label for="urgency">Urgency (1–5)</label><select id="urgency" name="urgency"><option>1</option><option>2</option><option>3</option><option>4</option><option selected>5</option></select></div><div><label for="accessibility">Accessibility impact (1–5)</label><select id="accessibility" name="accessibility"><option>1</option><option>2</option><option>3</option><option>4</option><option selected>5</option></select></div><div><label for="disruption">Safety/service impact (1–5)</label><select id="disruption" name="disruption"><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select></div><div><label for="recurrence">Recurrence (1–5)</label><select id="recurrence" name="recurrence"><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select></div></div><button type="submit">Submit report</button></form></section>
<section class="card"><h2>Recent reports</h2><p class="muted">Track submitted concerns and their current status. Priority is a prototype aid, not an automated final decision.</p>
{% if reports %}{% for r in reports %}<div class="report"><strong>#{{ r.id }} · {{ r.title }}</strong><div class="muted">{{ r.location }} · {{ r.category }}</div><p class="muted">{{ r.description }}</p><span class="pill">Priority {{ r.priority }}/100</span> <span class="pill">{{ r.status }}</span></div>{% endfor %}{% else %}<p class="muted">No reports yet. You can submit the first report using the form.</p>{% endif %}</section></div>
</main><div class="footer">CampusLens AI · Student prototype · Not an emergency response service</div></body></html>
"""

@app.get("/")
def home():
    with get_db() as conn:
        reports = conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 20").fetchall()
    return render_template_string(PAGE, reports=reports)

@app.post("/report")
def report():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    category = request.form.get("category", "Other")
    if not title or not description or not location:
        flash("Please complete all required fields.")
        return redirect(url_for("home"))
    try:
        scores = [max(1, min(5, int(request.form.get(k, "1")))) for k in ("urgency", "accessibility", "disruption", "recurrence")]
    except ValueError:
        flash("Please use valid scores.")
        return redirect(url_for("home"))
    priority = round((scores[0]*.4 + scores[1]*.3 + scores[2]*.2 + scores[3]*.1) * 20)
    with get_db() as conn:
        cur = conn.execute("INSERT INTO reports(title,description,location,category,urgency,accessibility,disruption,recurrence,priority,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (title[:120], description[:2000], location[:160], category, *scores, priority, "Submitted", datetime.now(timezone.utc).isoformat()))
        report_id = cur.lastrowid
    flash(f"Report submitted successfully. Your report ID is #{report_id}.")
    return redirect(url_for("home"))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
