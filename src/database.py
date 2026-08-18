import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "disaster_response.db")


def get_connection():
    connection = sqlite3.connect(DATABASE, timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def initialize_database():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                priority TEXT NOT NULL,
                victims INTEGER NOT NULL,
                description TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sos_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sos_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sos_id INTEGER NOT NULL,
                resource_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'ASSIGNED',
                FOREIGN KEY (sos_id) REFERENCES sos_reports(id),
                FOREIGN KEY (resource_id) REFERENCES resources(id)
            )
        """)

        connection.commit()
    finally:
        connection.close()


def seed_database():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM incidents")

        if cursor.fetchone()[0] == 0:
            incidents = [
                (
                    "Flooded Residential Area",
                    "Greater Noida",
                    "CRITICAL",
                    24,
                    "Multiple residents reported trapped households and rising water levels.",
                    28.4744,
                    77.5040
                ),
                (
                    "Road Infrastructure Damage",
                    "Noida",
                    "HIGH",
                    8,
                    "Major road section damaged, affecting emergency vehicle movement.",
                    28.5355,
                    77.3910
                ),
                (
                    "Medical Assistance Required",
                    "Delhi NCR",
                    "MEDIUM",
                    5,
                    "Citizens requesting medical assistance and emergency supplies.",
                    28.6139,
                    77.2090
                )
            ]

            cursor.executemany("""
                INSERT INTO incidents
                (title, location, priority, victims, description, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, incidents)

        cursor.execute("SELECT COUNT(*) FROM sos_reports")

        if cursor.fetchone()[0] == 0:
            sos_reports = [
                (
                    "Citizen SOS #1042",
                    "Greater Noida",
                    "Family trapped inside a residential building."
                ),
                (
                    "Citizen SOS #1043",
                    "Noida",
                    "Road blocked and ambulance access required."
                ),
                (
                    "Citizen SOS #1044",
                    "Delhi NCR",
                    "Medical supplies urgently required."
                )
            ]

            cursor.executemany("""
                INSERT INTO sos_reports
                (name, location, message)
                VALUES (?, ?, ?)
            """, sos_reports)

        cursor.execute("SELECT COUNT(*) FROM resources")

        if cursor.fetchone()[0] == 0:
            resources = [
                (
                    "AMBULANCE",
                    "Ambulance Team A1",
                    "Greater Noida",
                    28.4748,
                    77.5025,
                    "AVAILABLE"
                ),
                (
                    "RESCUE TEAM",
                    "Rescue Team R1",
                    "Noida",
                    28.5355,
                    77.3910,
                    "DEPLOYED"
                ),
                (
                    "MEDICAL",
                    "Emergency Medical Unit M1",
                    "Delhi NCR",
                    28.6139,
                    77.2090,
                    "AVAILABLE"
                ),
                (
                    "VOLUNTEERS",
                    "Volunteer Group V1",
                    "Greater Noida",
                    28.4700,
                    77.5000,
                    "ACTIVE"
                )
            ]

            cursor.executemany("""
                INSERT INTO resources
                (resource_type, name, location, latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, resources)

        connection.commit()
    except Exception as e:
        connection.rollback()
        print("Seeding exception handled:", e)
    finally:
        connection.close()


_db_initialized = False


def ensure_database_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            initialize_database()
            seed_database()
            _db_initialized = True
        except Exception as e:
            print("Database setup exception:", e)
