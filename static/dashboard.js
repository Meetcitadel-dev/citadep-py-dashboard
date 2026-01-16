const API_BASE = 'http://localhost:5001/api';

let charts = {};

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching metrics:', error);
        document.body.innerHTML = `
            <div class="container">
                <div class="loading">
                    <h2>Error loading dashboard</h2>
                    <p>${error.message}</p>
                    <p>Make sure the API server is running on port 5001</p>
                </div>
            </div>
        `;
        throw error;
    }
}

function updateStatCards(data) {
    document.getElementById('total-users').textContent = data.users?.total_users || '-';
    document.getElementById('dau').textContent = Object.values(data.sessions?.dau_by_date || {}).pop() || '-';
    document.getElementById('total-sessions').textContent = data.sessions?.total_sessions || '-';
    document.getElementById('total-vibes').textContent = data.vibes?.total_vibes_sent || '-';
    document.getElementById('total-matches').textContent = data.matches?.total_matches || '-';
    document.getElementById('total-messages').textContent = data.messages?.total_messages || '-';
    document.getElementById('mrr').textContent = `₹${data.revenue?.mrr || 0}`;
    document.getElementById('match-rate').textContent = `${(data.matches?.vibe_to_match_rate || 0).toFixed(1)}%`;
}

function createLineChart(canvasId, label, dates, values, color = '#667eea') {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: label,
                data: values,
                borderColor: color,
                backgroundColor: color + '20',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

function createBarChart(canvasId, label, labels, values, color = '#667eea') {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: color + '80',
                borderColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

function createPieChart(canvasId, labels, values, colors) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function createDoughnutChart(canvasId, labels, values, colors) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function updateCharts(data) {
    // DAU Chart
    const dauDates = Object.keys(data.sessions?.dau_by_date || {}).sort();
    const dauValues = dauDates.map(date => data.sessions.dau_by_date[date]);
    createLineChart('dau-chart', 'Daily Active Users', dauDates, dauValues, '#667eea');

    // Sessions Chart
    const sessionDates = Object.keys(data.sessions?.sessions_by_date || {}).sort();
    const sessionValues = sessionDates.map(date => data.sessions.sessions_by_date[date]);
    createLineChart('sessions-chart', 'Sessions', sessionDates, sessionValues, '#764ba2');

    // Vibes Chart
    const vibeDates = Object.keys(data.vibes?.vibes_by_date || {}).sort();
    const vibeValues = vibeDates.map(date => data.vibes.vibes_by_date[date]);
    createLineChart('vibes-chart', 'Vibes Sent', vibeDates, vibeValues, '#f093fb');

    // Matches Chart
    const matchDates = Object.keys(data.matches?.matches_by_date || {}).sort();
    const matchValues = matchDates.map(date => data.matches.matches_by_date[date]);
    createLineChart('matches-chart', 'Matches Created', matchDates, matchValues, '#4facfe');

    // Messages Chart
    const messageDates = Object.keys(data.messages?.messages_by_date || {}).sort();
    const messageValues = messageDates.map(date => data.messages.messages_by_date[date]);
    createLineChart('messages-chart', 'Messages Sent', messageDates, messageValues, '#43e97b');

    // Activity Heatmap
    const activityHours = Object.keys(data.activity?.activity_by_hour || {}).sort((a, b) => parseInt(a) - parseInt(b));
    const activityValues = activityHours.map(hour => data.activity.activity_by_hour[hour]);
    createBarChart('activity-chart', 'Activity by Hour', activityHours.map(h => `${h}:00`), activityValues, '#fa709a');

    // Funnel Chart
    const funnelLabels = ['Signups', 'Profile Complete', 'First Vibe', 'Match Created', 'First Message'];
    const funnelValues = [
        data.funnel?.signups || 0,
        data.funnel?.profile_complete || 0,
        data.funnel?.first_vibe_sent || 0,
        data.funnel?.match_created || 0,
        data.funnel?.first_message || 0
    ];
    createBarChart('funnel-chart', 'User Journey', funnelLabels, funnelValues, '#30cfd0');

    // Gender Chart
    const genderLabels = Object.keys(data.demographics?.gender || {});
    const genderValues = Object.values(data.demographics?.gender || {});
    createDoughnutChart('gender-chart', genderLabels, genderValues, ['#667eea', '#f093fb']);

    // Academic Year Chart
    const academicLabels = Object.keys(data.demographics?.academic_year || {});
    const academicValues = Object.values(data.demographics?.academic_year || {});
    createBarChart('academic-chart', 'Users', academicLabels, academicValues, '#4facfe');

    // Adjectives Chart
    const adjLabels = Object.keys(data.vibes?.vibes_by_adjective || {}).slice(0, 10);
    const adjValues = adjLabels.map(adj => data.vibes.vibes_by_adjective[adj]);
    createBarChart('adjectives-chart', 'Count', adjLabels, adjValues, '#fa709a');

    // Conversation Depth
    const depthLabels = Object.keys(data.conversations?.depth_distribution || {});
    const depthValues = Object.values(data.conversations?.depth_distribution || {});
    createBarChart('conversation-depth-chart', 'Conversations', depthLabels, depthValues, '#43e97b');

    // Premium vs Free
    const premiumLabels = ['Free', 'Premium'];
    const premiumValues = [
        data.users?.free_users || 0,
        data.users?.premium_users || 0
    ];
    createDoughnutChart('premium-chart', premiumLabels, premiumValues, ['#667eea', '#764ba2']);
}

function updateTables(data) {
    // Revenue Table
    const revenueTbody = document.querySelector('#revenue-table tbody');
    revenueTbody.innerHTML = `
        <tr><td>MRR</td><td>₹${data.revenue?.mrr || 0}</td></tr>
        <tr><td>Average LTV</td><td>₹${(data.revenue?.avg_ltv || 0).toFixed(2)}</td></tr>
        <tr><td>Total Revenue</td><td>₹${data.revenue?.total_revenue || 0}</td></tr>
        <tr><td>Premium Users</td><td>${data.users?.premium_users || 0}</td></tr>
    `;

    // Session Table
    const sessionTbody = document.querySelector('#session-table tbody');
    sessionTbody.innerHTML = `
        <tr><td>Total Sessions</td><td>${data.sessions?.total_sessions || 0}</td></tr>
        <tr><td>Avg Session Duration</td><td>${(data.sessions?.avg_session_duration_minutes || 0).toFixed(2)} min</td></tr>
        <tr><td>Avg Sessions/User/Day</td><td>${Object.values(data.sessions?.avg_sessions_per_user_per_day || {}).pop()?.toFixed(1) || '-'}</td></tr>
    `;

    // Message Table
    const messageTbody = document.querySelector('#message-table tbody');
    messageTbody.innerHTML = `
        <tr><td>Total Messages</td><td>${data.messages?.total_messages || 0}</td></tr>
        <tr><td>Response Rate</td><td>${(data.messages?.response_rate || 0).toFixed(1)}%</td></tr>
        <tr><td>Avg Response Time</td><td>${(data.messages?.avg_response_time_minutes || 0).toFixed(1)} min</td></tr>
        <tr><td>Total Conversations</td><td>${data.conversations?.total_conversations || 0}</td></tr>
    `;
}

async function initDashboard() {
    try {
        const data = await fetchMetrics();
        updateStatCards(data);
        updateCharts(data);
        updateTables(data);
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
}

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', initDashboard);

// Refresh every 30 seconds
setInterval(initDashboard, 30000);
