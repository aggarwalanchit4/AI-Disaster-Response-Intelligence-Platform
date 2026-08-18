from flask import Flask, jsonify, render_template, request
from database import (
    ensure_database_initialized,
    get_connection,
    initialize_database,
    seed_database
)

app = Flask(__name__)

# Initialize and seed database on application startup (works for both Gunicorn WSGI & direct CLI)
ensure_database_initialized()


@app.before_request
def setup_database_before_request():
    ensure_database_initialized()


@app.route("/")


def home():
    return render_template("index.html")


@app.route("/api/incidents")
def get_incidents():
    connection = get_connection()
    incidents = connection.execute("""
        SELECT * FROM incidents
        ORDER BY
            CASE priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                ELSE 4
            END,
            victims DESC
    """).fetchall()
    connection.close()

    return jsonify([dict(incident) for incident in incidents])


def calculate_sos_priority(description):
    text = description.lower()

    critical_keywords = [
        "trapped", "drowning", "drowned", "critical", "unconscious",
        "life threatening", "immediate rescue", "people trapped", "family trapped"
    ]
    high_keywords = [
        "injured", "injury", "fire", "ambulance", "blocked", "urgent",
        "rescue required", "emergency"
    ]
    medium_keywords = [
        "medical", "medicine", "supplies", "help needed", "assistance"
    ]

    for keyword in critical_keywords:
        if keyword in text:
            return "CRITICAL"
    for keyword in high_keywords:
        if keyword in text:
            return "HIGH"
    for keyword in medium_keywords:
        if keyword in text:
            return "MEDIUM"

    return "LOW"


@app.route("/api/sos")
def get_sos_reports():
    connection = get_connection()
    reports = connection.execute("""
        SELECT
            s.*,
            a.id AS assignment_id,
            a.resource_id AS assigned_resource_id,
            r.name AS assigned_resource_name,
            r.resource_type AS assigned_resource_type
        FROM sos_reports s
        LEFT JOIN sos_assignments a
            ON s.id = a.sos_id AND a.status = 'ASSIGNED'
        LEFT JOIN resources r
            ON a.resource_id = r.id
        ORDER BY s.id DESC
    """).fetchall()
    sos_reports = []

    for report in reports:
        report_data = dict(report)
        report_data["priority"] = calculate_sos_priority(
            report_data["message"]
        )
        sos_reports.append(report_data)

    connection.close()

    return jsonify(sos_reports)



@app.route("/api/sos", methods=["POST"])
def create_sos_report():
    data = request.get_json()

    name = data.get("name", "").strip()
    location = data.get("location", "").strip()
    message = data.get("message", "").strip()

    if not name or not location or not message:
        return jsonify({
            "error": "All SOS fields are required."
        }), 400

    connection = get_connection()

    connection.execute("""
        INSERT INTO sos_reports
        (name, location, message)
        VALUES (?, ?, ?)
    """, (name, location, message))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "SOS report received successfully."
    }), 201


@app.route("/api/resources")
def get_resources():
    connection = get_connection()

    resources = connection.execute("""
        SELECT *
        FROM resources
        ORDER BY resource_type, name
    """).fetchall()

    connection.close()

    return jsonify([
        dict(resource)
        for resource in resources
    ])


@app.route("/api/resources/<int:resource_id>/status", methods=["PUT"])
def update_resource_status(resource_id):
    data = request.get_json()

    status = data.get("status", "").strip().upper()

    allowed_statuses = [
        "AVAILABLE",
        "DEPLOYED",
        "ACTIVE",
        "OFFLINE"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid resource status."
        }), 400

    connection = get_connection()

    resource = connection.execute("""
        SELECT *
        FROM resources
        WHERE id = ?
    """, (resource_id,)).fetchone()

    if resource is None:
        connection.close()

        return jsonify({
            "error": "Resource not found."
        }), 404

    connection.execute("""
        UPDATE resources
        SET status = ?
        WHERE id = ?
    """, (status, resource_id))

    connection.commit()

    updated_resource = connection.execute("""
        SELECT *
        FROM resources
        WHERE id = ?
    """, (resource_id,)).fetchone()

    connection.close()

    return jsonify({
        "message": "Resource status updated successfully.",
        "resource": dict(updated_resource)
    })


@app.route("/api/sos/<int:sos_id>/assign", methods=["POST"])
def assign_resource_to_sos(sos_id):
    data = request.get_json()

    resource_id = data.get("resource_id")

    if not resource_id:
        return jsonify({
            "error": "Resource ID is required."
        }), 400

    connection = get_connection()

    sos = connection.execute("""
        SELECT *
        FROM sos_reports
        WHERE id = ?
    """, (sos_id,)).fetchone()

    if sos is None:
        connection.close()

        return jsonify({
            "error": "SOS report not found."
        }), 404

    resource = connection.execute("""
        SELECT *
        FROM resources
        WHERE id = ?
    """, (resource_id,)).fetchone()

    if resource is None:
        connection.close()

        return jsonify({
            "error": "Resource not found."
        }), 404

    if resource["status"] == "DEPLOYED":
        connection.close()

        return jsonify({
            "error": "Resource is already deployed."
        }), 409

    existing_assignment = connection.execute("""
        SELECT *
        FROM sos_assignments
        WHERE sos_id = ?
        AND status = 'ASSIGNED'
    """, (sos_id,)).fetchone()

    if existing_assignment:
        connection.close()

        return jsonify({
            "error": "This SOS already has an assigned resource."
        }), 409

    cursor = connection.execute("""
        INSERT INTO sos_assignments
        (sos_id, resource_id, status)
        VALUES (?, ?, 'ASSIGNED')
    """, (sos_id, resource_id))

    connection.execute("""
        UPDATE resources
        SET status = 'DEPLOYED'
        WHERE id = ?
    """, (resource_id,))

    connection.commit()

    assignment = connection.execute("""
        SELECT
            a.id,
            a.sos_id,
            a.resource_id,
            a.assigned_at,
            a.status,
            r.name AS resource_name,
            r.resource_type,
            s.name AS sos_name,
            s.location AS sos_location
        FROM sos_assignments a
        JOIN resources r
            ON a.resource_id = r.id
        JOIN sos_reports s
            ON a.sos_id = s.id
        WHERE a.id = ?
    """, (cursor.lastrowid,)).fetchone()

    connection.close()

    return jsonify({
        "message": "Resource assigned successfully.",
        "assignment": dict(assignment)
    }), 201


@app.route("/api/sos/<int:sos_id>/unassign", methods=["POST"])
def unassign_resource_from_sos(sos_id):
    connection = get_connection()

    assignment = connection.execute("""
        SELECT *
        FROM sos_assignments
        WHERE sos_id = ? AND status = 'ASSIGNED'
    """, (sos_id,)).fetchone()

    if assignment is None:
        connection.close()
        return jsonify({
            "error": "No active assignment found for this SOS report."
        }), 404

    resource_id = assignment["resource_id"]

    connection.execute("""
        UPDATE sos_assignments
        SET status = 'RELEASED'
        WHERE id = ?
    """, (assignment["id"],))

    connection.execute("""
        UPDATE resources
        SET status = 'AVAILABLE'
        WHERE id = ?
    """, (resource_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Resource released successfully."
    })


@app.route("/api/ai-summary")

def generate_ai_summary():
    connection = get_connection()

    incidents = connection.execute("""
        SELECT *
        FROM incidents
        ORDER BY
            CASE priority
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                ELSE 4
            END,
            victims DESC
    """).fetchall()

    sos_reports = connection.execute("""
        SELECT *
        FROM sos_reports
        ORDER BY id DESC
    """).fetchall()

    resources = connection.execute("""
        SELECT *
        FROM resources
    """).fetchall()

    connection.close()

    total_victims = sum(
        incident["victims"]
        for incident in incidents
    )

    critical_incidents = [
        incident
        for incident in incidents
        if incident["priority"] == "CRITICAL"
    ]

    high_incidents = [
        incident
        for incident in incidents
        if incident["priority"] == "HIGH"
    ]

    available_resources = [
        resource
        for resource in resources
        if resource["status"] == "AVAILABLE"
    ]

    deployed_resources = [
        resource
        for resource in resources
        if resource["status"] == "DEPLOYED"
    ]

    summary = {
        "active_incidents": len(incidents),
        "critical_incidents": len(critical_incidents),
        "high_priority_incidents": len(high_incidents),
        "reported_victims": total_victims,
        "sos_reports": len(sos_reports),
        "available_resources": len(available_resources),
        "deployed_resources": len(deployed_resources)
    }

    recommendations = []

    if critical_incidents:
        highest_priority = critical_incidents[0]

        recommendations.append(
            f"Prioritize immediate response to "
            f"{highest_priority['location']} where "
            f"{highest_priority['victims']} victims are reported."
        )

    if len(sos_reports) > 0:
        recommendations.append(
            f"Review {len(sos_reports)} citizen SOS reports "
            f"for additional rescue requirements."
        )

    if available_resources:
        recommendations.append(
            f"{len(available_resources)} response resources "
            f"are currently available for deployment."
        )

    if deployed_resources:
        recommendations.append(
            f"{len(deployed_resources)} resource(s) are already "
            f"deployed and should be monitored."
        )

    return jsonify({
        "summary": summary,
        "recommendations": recommendations
    })


@app.route("/api/stats")
def get_stats():
    connection = get_connection()
    incident_count = connection.execute(
        "SELECT COUNT(*) FROM incidents"
    ).fetchone()[0]
    critical_victims = connection.execute(
        "SELECT COALESCE(SUM(victims), 0) FROM incidents WHERE priority = 'CRITICAL'"
    ).fetchone()[0]
    sos_count = connection.execute(
        "SELECT COUNT(*) FROM sos_reports"
    ).fetchone()[0]
    connection.close()

    return jsonify({
        "incidents": incident_count,
        "critical_victims": critical_victims,
        "sos_reports": sos_count,
        "rescue_teams": 12,
        "volunteers": 47
    })


if __name__ == "__main__":
    app.run(debug=True)

