from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "spaceresearchdb2024"

# ── Database connection ───────────────────────────────────────────────────────
# Reads DATABASE_URL from environment variable (set on Render.com)
# For local testing, set it manually below
def get_db():
    url = os.environ.get("DATABASE_URL")
    conn = psycopg2.connect(url)
    return conn

def query(sql, params=(), one=False):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = cur.fetchone() if one else cur.fetchall()
    conn.close()
    return result

def execute(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    missions    = query("SELECT COUNT(*) as c FROM mission")[0]["c"]
    spacecraft  = query("SELECT COUNT(*) as c FROM spacecraft")[0]["c"]
    astronauts  = query("SELECT COUNT(*) as c FROM astronaut")[0]["c"]
    experiments = query("SELECT COUNT(*) as c FROM experiment")[0]["c"]
    recent = query("""
        SELECT m.missionid, m.mname, m.mstatus, m.launchdate,
               s.cname, cc.centername
        FROM mission m
        LEFT JOIN spacecraft s ON m.craftid = s.craftid
        LEFT JOIN control_center cc ON m.centerid = cc.centerid
        ORDER BY m.launchdate DESC
    """)
    return render_template("dashboard.html",
        mission_count=missions, spacecraft_count=spacecraft,
        astronaut_count=astronauts, experiment_count=experiments,
        recent_missions=recent)

# ── Missions ──────────────────────────────────────────────────────────────────
@app.route("/missions")
def missions():
    rows = query("""
        SELECT m.*, s.cname, cc.centername
        FROM mission m
        LEFT JOIN spacecraft s ON m.craftid = s.craftid
        LEFT JOIN control_center cc ON m.centerid = cc.centerid
        ORDER BY m.launchdate DESC
    """)
    spacecraft = query("SELECT craftid, cname FROM spacecraft ORDER BY cname")
    centers    = query("SELECT centerid, centername FROM control_center ORDER BY centername")
    return render_template("missions.html", missions=rows,
                           spacecraft=spacecraft, centers=centers)

@app.route("/missions/add", methods=["POST"])
def add_mission():
    try:
        execute("""INSERT INTO mission VALUES (%s,%s,%s,%s,%s,%s,%s)""", (
            request.form["missionId"], request.form["mName"],
            request.form["mStatus"], request.form["launchDate"],
            request.form["craftId"] or None, request.form["centerId"] or None,
            request.form["monitoringShift"] or None
        ))
        flash("Mission added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("missions"))

@app.route("/missions/delete/<id>")
def delete_mission(id):
    try:
        execute("DELETE FROM mission WHERE missionid = %s", (id,))
        flash("Mission deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("missions"))

# ── Spacecraft ────────────────────────────────────────────────────────────────
@app.route("/spacecraft")
def spacecraft():
    rows = query("SELECT * FROM spacecraft ORDER BY cname")
    return render_template("spacecraft.html", spacecraft=rows)

@app.route("/spacecraft/add", methods=["POST"])
def add_spacecraft():
    try:
        execute("INSERT INTO spacecraft VALUES (%s,%s,%s,%s,%s,%s,%s)", (
            request.form["craftId"], request.form["cName"],
            request.form["manufacturer"], request.form["fuelType"],
            request.form["length"] or None, request.form["width"] or None,
            request.form["height"] or None
        ))
        flash("Spacecraft added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("spacecraft"))

@app.route("/spacecraft/delete/<id>")
def delete_spacecraft(id):
    try:
        execute("DELETE FROM spacecraft WHERE craftid = %s", (id,))
        flash("Spacecraft deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("spacecraft"))

# ── Astronauts ────────────────────────────────────────────────────────────────
@app.route("/astronauts")
def astronauts():
    rows = query("""
        SELECT a.*, STRING_AGG(s.skill, ', ') as skills,
               DATE_PART('year', AGE(a.dob)) as age
        FROM astronaut a
        LEFT JOIN astronaut_skills s ON a.astronautid = s.astronautid
        GROUP BY a.astronautid, a.firstname, a.lastname, a.dob, a.nationality
        ORDER BY a.lastname
    """)
    return render_template("astronauts.html", astronauts=rows)

@app.route("/astronauts/add", methods=["POST"])
def add_astronaut():
    try:
        execute("INSERT INTO astronaut VALUES (%s,%s,%s,%s,%s)", (
            request.form["astronautId"], request.form["firstName"],
            request.form["lastName"], request.form["dob"],
            request.form["nationality"]
        ))
        skills = request.form.get("skills", "")
        for skill in [s.strip() for s in skills.split(",") if s.strip()]:
            execute("INSERT INTO astronaut_skills VALUES (%s,%s)",
                    (request.form["astronautId"], skill))
        flash("Astronaut added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("astronauts"))

@app.route("/astronauts/delete/<id>")
def delete_astronaut(id):
    try:
        execute("DELETE FROM astronaut WHERE astronautid = %s", (id,))
        flash("Astronaut deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("astronauts"))

# ── Experiments ───────────────────────────────────────────────────────────────
@app.route("/experiments")
def experiments():
    rows = query("""
        SELECT e.*, STRING_AGG(q.equipment, ', ') as equipment
        FROM experiment e
        LEFT JOIN exp_equip q ON e.expid = q.expid
        GROUP BY e.expid, e.expname, e.domain
        ORDER BY e.expname
    """)
    return render_template("experiments.html", experiments=rows)

@app.route("/experiments/add", methods=["POST"])
def add_experiment():
    try:
        execute("INSERT INTO experiment VALUES (%s,%s,%s)", (
            request.form["expId"], request.form["expName"], request.form["domain"]
        ))
        equipment = request.form.get("equipment", "")
        for eq in [e.strip() for e in equipment.split(",") if e.strip()]:
            execute("INSERT INTO exp_equip VALUES (%s,%s)",
                    (request.form["expId"], eq))
        flash("Experiment added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("experiments"))

@app.route("/experiments/delete/<id>")
def delete_experiment(id):
    try:
        execute("DELETE FROM experiment WHERE expid = %s", (id,))
        flash("Experiment deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("experiments"))

# ── Control Centers ───────────────────────────────────────────────────────────
@app.route("/centers")
def centers():
    rows = query("SELECT * FROM control_center ORDER BY centername")
    return render_template("centers.html", centers=rows)

@app.route("/centers/add", methods=["POST"])
def add_center():
    try:
        execute("INSERT INTO control_center VALUES (%s,%s,%s,%s)", (
            request.form["centerId"], request.form["centerName"],
            request.form["city"], request.form["country"]
        ))
        flash("Control center added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("centers"))

@app.route("/centers/delete/<id>")
def delete_center(id):
    try:
        execute("DELETE FROM control_center WHERE centerid = %s", (id,))
        flash("Center deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("centers"))

# ── Telemetry ─────────────────────────────────────────────────────────────────
@app.route("/telemetry")
def telemetry():
    rows = query("""
        SELECT t.*, m.mname FROM telemetry_data t
        LEFT JOIN mission m ON t.missionid = m.missionid
        ORDER BY t.transmissiontime DESC
    """)
    missions = query("SELECT missionid, mname FROM mission ORDER BY mname")
    return render_template("telemetry.html", telemetry=rows, missions=missions)

@app.route("/telemetry/add", methods=["POST"])
def add_telemetry():
    try:
        execute("INSERT INTO telemetry_data VALUES (%s,%s,%s,%s,%s)", (
            request.form["telemetryId"], request.form["signalStrength"],
            request.form["transmissionTime"], request.form["temperature"],
            request.form["missionId"]
        ))
        flash("Telemetry logged!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("telemetry"))

if __name__ == "__main__":
    app.run(debug=True)
