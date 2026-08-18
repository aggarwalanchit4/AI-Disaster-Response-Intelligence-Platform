let incidents = [];
let sosReports = [];
let resources = [];
let map;
let markerLayer;

async function loadDashboard() {
    try {
        const [
            incidentsResponse,
            sosResponse,
            statsResponse,
            resourcesResponse
        ] = await Promise.all([
            fetch("/api/incidents"),
            fetch("/api/sos"),
            fetch("/api/stats"),
            fetch("/api/resources")
        ]);

        incidents = await incidentsResponse.json();
        sosReports = await sosResponse.json();
        resources = await resourcesResponse.json();
        const stats = await statsResponse.json();

        updateStatistics(stats);
        updateMap();
        updateIncidentList();
        updateSOSList();
        updateResourceList();
    } catch (error) {
        console.error("Failed to load dashboard data:", error);
    }
}

function updateStatistics(stats) {
    document.getElementById("incidentCount").textContent = stats.incidents;
    document.getElementById("criticalCount").textContent = stats.critical_victims;
    document.getElementById("teamCount").textContent = stats.rescue_teams;
    document.getElementById("volunteerCount").textContent = stats.volunteers;
}

let legendControl;

function initializeMap() {
    map = L.map("map").setView([28.55, 77.35], 10);
    markerLayer = L.layerGroup().addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    addMapLegend();
}

function addMapLegend() {
    if (legendControl) return;

    legendControl = L.control({ position: 'bottomright' });

    legendControl.onAdd = function () {
        const div = L.DomUtil.create('div', 'map-legend-box');
        div.innerHTML = `
            <div class="legend-header">Map Legend</div>
            <div class="legend-grid">
                <div class="legend-col">
                    <strong>Incidents</strong>
                    <div><span class="legend-icon">🔴</span> Critical</div>
                    <div><span class="legend-icon">🟠</span> High</div>
                    <div><span class="legend-icon">🔵</span> Medium</div>
                </div>
                <div class="legend-col">
                    <strong>Resources</strong>
                    <div><span class="legend-icon">🚑</span> Ambulance</div>
                    <div><span class="legend-icon">🚒</span> Rescue Team</div>
                    <div><span class="legend-icon">🏥</span> Medical</div>
                    <div><span class="legend-icon">👥</span> Volunteers</div>
                </div>
            </div>
        `;
        return div;
    };

    legendControl.addTo(map);
}

function createMarkerIcon(type) {
    let emoji = "📍";

    if (type === "CRITICAL") {
        emoji = "🔴";
    } else if (type === "HIGH") {
        emoji = "🟠";
    } else if (type === "MEDIUM") {
        emoji = "🔵";
    } else if (type === "AMBULANCE") {
        emoji = "🚑";
    } else if (type === "RESCUE TEAM") {
        emoji = "🚒";
    } else if (type === "MEDICAL") {
        emoji = "🏥";
    } else if (type === "VOLUNTEERS") {
        emoji = "👥";
    }

    return L.divIcon({
        className: "custom-map-marker",
        html: `<div class="map-marker">${emoji}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
        popupAnchor: [0, -18]
    });
}

function updateMap() {
    if (!map) {
        initializeMap();
    }

    markerLayer.clearLayers();

    const bounds = [];

    incidents.forEach(incident => {
        const position = [
            incident.latitude,
            incident.longitude
        ];

        bounds.push(position);

        const marker = L.marker(position, {
            icon: createMarkerIcon(incident.priority)
        }).addTo(markerLayer);

        marker.bindPopup(`
            <strong>🚨 ${incident.title}</strong><br>
            Location: ${incident.location}<br>
            Priority: ${incident.priority}<br>
            Victims: ${incident.victims}
        `);
    });

    resources.forEach(resource => {
        const position = [
            resource.latitude,
            resource.longitude
        ];

        bounds.push(position);

        const marker = L.marker(position, {
            icon: createMarkerIcon(resource.resource_type)
        }).addTo(markerLayer);

        marker.bindPopup(`
            <strong>🚑 ${resource.name}</strong><br>
            Type: ${resource.resource_type}<br>
            Location: ${resource.location}<br>
            Status: ${resource.status}
        `);
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, {
            padding: [40, 40]
        });
    }
}

function updateIncidentList() {
    const incidentList = document.getElementById("incidentList");
    incidentList.innerHTML = "";

    if (incidents.length === 0) {
        incidentList.innerHTML = `
            <div class="empty-state">
                No active incidents
            </div>
        `;
        return;
    }

    incidents.forEach(incident => {
        let priorityClass;

        if (incident.priority === "CRITICAL") {
            priorityClass = "priority-critical";
        } else if (incident.priority === "HIGH") {
            priorityClass = "priority-high";
        } else {
            priorityClass = "priority-medium";
        }

        const card = document.createElement("div");
        card.className = "incident";
        card.innerHTML = `
            <div class="incident-top">
                <div class="incident-title">${incident.title}</div>
                <span class="priority ${priorityClass}">${incident.priority}</span>
            </div>
            <p><strong>Location:</strong> ${incident.location}</p>
            <p><strong>Victims:</strong> ${incident.victims}</p>
            <p>${incident.description}</p>
        `;

        incidentList.appendChild(card);
    });
}

function updateSOSList() {
    const sosList = document.getElementById("sosList");
    sosList.innerHTML = "";

    if (sosReports.length === 0) {
        sosList.innerHTML = `
            <div class="empty-state">
                No SOS reports received.
            </div>
        `;
        return;
    }

    const priorityOrder = {
        CRITICAL: 1,
        HIGH: 2,
        MEDIUM: 3,
        LOW: 4
    };

    const sortedReports = [...sosReports].sort((a, b) => {
        return (
            (priorityOrder[a.priority] || 5) -
            (priorityOrder[b.priority] || 5)
        );
    });

    const availableResources = resources.filter(r => r.status === "AVAILABLE");

    sortedReports.forEach(report => {
        const card = document.createElement("div");
        card.className = "sos-report";
        const priority = report.priority || "LOW";
        const priorityClass = priority.toLowerCase();

        let assignmentHtml = "";

        if (report.assigned_resource_name) {
            assignmentHtml = `
                <div class="sos-assignment-row">
                    <span class="assignment-badge">
                        ✅ Assigned: <strong>${report.assigned_resource_name}</strong> (${report.assigned_resource_type})
                    </span>
                    <button class="release-btn" data-sos-id="${report.id}">
                        Release Resource
                    </button>
                </div>
            `;
        } else {
            let optionsHtml = `<option value="">-- Select Available Resource --</option>`;
            availableResources.forEach(res => {
                optionsHtml += `<option value="${res.id}">${res.name} (${res.resource_type} - ${res.location})</option>`;
            });

            if (availableResources.length > 0) {
                assignmentHtml = `
                    <div class="sos-assignment-row">
                        <select class="assign-select" id="assignSelect-${report.id}">
                            ${optionsHtml}
                        </select>
                        <button class="assign-btn" data-sos-id="${report.id}">
                            Assign Resource
                        </button>
                    </div>
                `;
            } else {
                assignmentHtml = `
                    <div class="sos-assignment-row">
                        <span class="no-resources-msg">⚠️ No response resources currently available.</span>
                    </div>
                `;
            }
        }

        card.innerHTML = `
            <div class="sos-header">
                <div>
                    <h3>${report.name}</h3>
                    <p><strong>Location:</strong> ${report.location}</p>
                </div>
                <span class="sos-priority ${priorityClass}">
                    ${priority}
                </span>
            </div>
            <p class="sos-message-text">${report.message}</p>
            ${assignmentHtml}
        `;

        sosList.appendChild(card);
    });

    document.querySelectorAll(".assign-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const sosId = btn.dataset.sosId;
            const selectEl = document.getElementById(`assignSelect-${sosId}`);
            const resourceId = selectEl.value;

            if (!resourceId) {
                alert("Please select an available resource from the dropdown first.");
                return;
            }

            await assignResource(sosId, resourceId);
        });
    });

    document.querySelectorAll(".release-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const sosId = btn.dataset.sosId;
            await unassignResource(sosId);
        });
    });
}

async function assignResource(sosId, resourceId) {
    try {
        const response = await fetch(`/api/sos/${sosId}/assign`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ resource_id: parseInt(resourceId, 10) })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to assign resource.");
        }

        await loadDashboard();
    } catch (error) {
        console.error("Assignment error:", error);
        alert("Unable to assign resource: " + error.message);
    }
}

async function unassignResource(sosId) {
    try {
        const response = await fetch(`/api/sos/${sosId}/unassign`, {
            method: "POST"
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to release resource.");
        }

        await loadDashboard();
    } catch (error) {
        console.error("Release error:", error);
        alert("Unable to release resource: " + error.message);
    }
}


function updateResourceList() {
    const resourceList = document.getElementById("resourceList");
    resourceList.innerHTML = "";

    if (resources.length === 0) {
        resourceList.innerHTML = `
            <div class="empty-state">
                No response resources available.
            </div>
        `;
        return;
    }

    resources.forEach(resource => {
        let icon = "📍";

        if (resource.resource_type === "AMBULANCE") {
            icon = "🚑";
        } else if (resource.resource_type === "RESCUE TEAM") {
            icon = "🚒";
        } else if (resource.resource_type === "MEDICAL") {
            icon = "🏥";
        } else if (resource.resource_type === "VOLUNTEERS") {
            icon = "👥";
        }

        const card = document.createElement("div");
        card.className = "resource-card";

        const canDeploy = resource.status === "AVAILABLE";
        const buttonText = canDeploy ? "Deploy" : "Mark Available";
        const nextStatus = canDeploy ? "DEPLOYED" : "AVAILABLE";

        card.innerHTML = `
            <div class="resource-info">
                <div class="resource-title">${icon} ${resource.name}</div>
                <p><strong>Type:</strong> ${resource.resource_type}</p>
                <p><strong>Location:</strong> ${resource.location}</p>
                <p>
                    <strong>Status:</strong>
                    <span class="resource-status">${resource.status}</span>
                </p>
            </div>
            <button
                class="resource-button"
                data-id="${resource.id}"
                data-status="${nextStatus}"
            >
                ${buttonText}
            </button>
        `;

        resourceList.appendChild(card);
    });

    document.querySelectorAll(".resource-button").forEach(button => {
        button.addEventListener("click", () => updateResourceStatus(
            button.dataset.id,
            button.dataset.status
        ));
    });
}

async function updateResourceStatus(resourceId, newStatus) {
    try {
        const response = await fetch(
            `/api/resources/${resourceId}/status`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to update resource.");
        }

        await loadDashboard();
    } catch (error) {
        console.error("Resource update error:", error);
        alert("Unable to update resource status.");
    }
}

document.getElementById("generateSummary").addEventListener("click", async () => {
    const button = document.getElementById("generateSummary");
    const output = document.getElementById("aiSummary");

    button.disabled = true;
    button.textContent = "Analyzing...";
    output.textContent = "AI Disaster Intelligence is analyzing current incidents, SOS reports and response resources...";

    try {
        const response = await fetch("/api/ai-summary");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to generate summary.");
        }

        const summary = data.summary;
        const recommendations = data.recommendations;
        let text = `Situation Overview\n\n`
            + `Active incidents: ${summary.active_incidents}\n`
            + `Critical incidents: ${summary.critical_incidents}\n`
            + `High-priority incidents: ${summary.high_priority_incidents}\n`
            + `Reported victims: ${summary.reported_victims}\n`
            + `Citizen SOS reports: ${summary.sos_reports}\n`
            + `Available resources: ${summary.available_resources}\n`
            + `Deployed resources: ${summary.deployed_resources}\n\n`
            + `Recommended Actions\n\n`;

        recommendations.forEach((recommendation, index) => {
            text += `${index + 1}. ${recommendation}\n`;
        });

        output.textContent = text;
    } catch (error) {
        console.error("AI summary error:", error);
        output.textContent = "Unable to generate AI intelligence. "
            + "Please check the Flask server.";
    } finally {
        button.disabled = false;
        button.textContent = "Generate Summary";
    }
});

loadDashboard();

document.getElementById("sosForm").addEventListener("submit", async event => {
    event.preventDefault();

    const name = document.getElementById("sosName").value.trim();
    const location = document.getElementById("sosLocation").value.trim();
    const message = document.getElementById("sosMessage").value.trim();
    const status = document.getElementById("sosStatus");

    status.textContent = "Submitting SOS...";

    try {
        const response = await fetch("/api/sos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, location, message })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Failed to submit SOS.");
        }

        status.textContent = "✅ SOS report submitted successfully.";
        document.getElementById("sosForm").reset();
        await loadDashboard();
    } catch (error) {
        console.error(error);
        status.textContent = "❌ " + error.message;
    }
});

// ------------------------------------
// REAL-TIME DATA REFRESH
// ------------------------------------

setInterval(async function () {
    await loadDashboard();
}, 10000);
