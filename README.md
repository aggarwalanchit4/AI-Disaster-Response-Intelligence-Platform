# 🚨 AI Disaster Response Intelligence Platform

> **Automate India Hackathon Project Submission**  
> An end-to-end, real-time command center platform designed to automate disaster triage, citizen emergency SOS dispatching, GIS resource tracking, and AI situation synthesis.

---

## 🌟 Overview

During large-scale natural disasters and civil emergencies, command centers face severe information overload and response delays. The **AI Disaster Response Intelligence Platform** unifies citizen emergency requests, priority incident tracking, and response asset management into an interactive, intelligent command center.

It automatically prioritizes citizen SOS requests based on emergency severity keywords, renders real-time location markers on an interactive GIS map, and streamlines resource assignment—ensuring fast, coordinated rescue operations.

---

## 🔥 Key Features

- **🌐 Interactive Real-Time GIS Map**: Built with Leaflet.js featuring custom color-coded map markers for critical/high/medium incidents and emergency response teams (Ambulance, Rescue, Medical, Volunteers), plus a live Map Legend.
- **🚨 Citizen SOS Emergency Portal**: Direct emergency reporting interface with automatic backend keyword-based priority classification (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **🚑 SOS → Resource Assignment Workflow**: Instant allocation of available response units to incoming emergency SOS reports. Selecting and assigning a resource updates unit status to `DEPLOYED` and updates all dashboard metrics.
- **📊 Real-Time Command Dashboard**: Live statistics counter tracking active disaster zones, critical victim counts, active rescue teams, and registered volunteers.
- **🤖 AI Disaster Intelligence**: One-click and automated situation synthesis summarizing active casualty counts, unassigned emergency requests, and generating prioritized actionable recommendations for dispatchers.
- **🔄 Live Auto-Refresh**: Background synchronization keeps disaster controllers up-to-date with current database states.

---

## 🏗 System Architecture

```text
       ┌─────────────────────────────────────────────────────────┐
       │                Browser Web Dashboard                    │
       │     (HTML5 / CSS3 Dark Theme / Leaflet GIS / JS)        │
       └───────────────────────────┬─────────────────────────────┘
                                   │  HTTP / REST API
                                   ▼
       ┌─────────────────────────────────────────────────────────┐
       │                   Flask Application                     │
       │                   (Python Backend)                      │
       └─────┬─────────────────────┬───────────────────────┬─────┘
             │                     │                       │
             ▼                     ▼                       ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────┐
    │ Priority Triage │   │ Resource Engine │   │ AI Situation Engine│
    └────────┬────────┘   └────────┬────────┘   └─────────┬──────────┘
             │                     │                      │
             └─────────────────────┼──────────────────────┘
                                   │
                                   ▼
       ┌─────────────────────────────────────────────────────────┐
       │                  SQLite Database                        │
       │  (incidents, sos_reports, resources, sos_assignments)   │
       └─────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```text
AI-Disaster-Response-Intelligence-Platform/
├── presentation/
│   └── AI-Disaster-Response-Intelligence-Platform.pdf  # Project Presentation PDF
├── src/
│   ├── static/
│   │   ├── script.js             # Dashboard UI logic & API integrations
│   │   └── style.css             # Command-center styling & responsive layout
│   ├── templates/
│   │   └── index.html            # Main command center template
│   ├── app.py                    # Flask application server & REST endpoints
│   ├── database.py               # SQLite schema & database initialization
│   └── requirements.txt          # Python dependencies
├── .gitignore                    # Version control exclusion rules
├── README.md                     # Project documentation
└── requirements.txt              # Root Python dependencies
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.9+** installed on your system.

### Installation & Execution

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/AI-Disaster-Response-Intelligence-Platform.git
   cd AI-Disaster-Response-Intelligence-Platform
   ```

2. **Set up Virtual Environment**:
   - **Windows**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Flask Server**:
   ```bash
   python src/app.py
   ```

5. **Open Dashboard**:
   Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | `GET` | Render main command center web interface |
| `GET /api/incidents` | `GET` | Retrieve priority incidents sorted by severity & victim count |
| `GET /api/sos` | `GET` | Retrieve citizen SOS reports with assignment details & priority |
| `POST /api/sos` | `POST` | Submit a new citizen emergency report |
| `GET /api/resources` | `GET` | Fetch emergency response units and operational status |
| `PUT /api/resources/<id>/status` | `PUT` | Update response unit status (`AVAILABLE`, `DEPLOYED`, `ACTIVE`, `OFFLINE`) |
| `POST /api/sos/<id>/assign` | `POST` | Assign an available resource unit to an emergency SOS report |
| `POST /api/sos/<id>/unassign` | `POST` | Release an assigned resource unit back to `AVAILABLE` |
| `GET /api/ai-summary` | `GET` | Generate AI situation overview & prioritized recommendations |
| `GET /api/stats` | `GET` | Fetch top-level command metrics |

---

## 🗄 Database Schema

The system uses an SQLite database (`disaster_response.db`) containing four relational tables:

- **`incidents`**: Stores disaster events, locations, coordinates, priority levels, and casualty numbers.
- **`sos_reports`**: Stores incoming citizen emergency requests with name, location, and message text.
- **`resources`**: Stores response units (Ambulance, Rescue, Medical, Volunteers), coordinates, and status.
- **`sos_assignments`**: Maps SOS reports to assigned response units with assignment timestamps and status (`ASSIGNED`, `RELEASED`).

---

## 📄 Presentation

The project presentation is available in the repository at:  
👉 **[`presentation/AI-Disaster-Response-Intelligence-Platform.pdf`](presentation/AI-Disaster-Response-Intelligence-Platform.pdf)**

---

## 🛡 License & Attribution

Developed for the **Automate India Hackathon**. All rights reserved.
