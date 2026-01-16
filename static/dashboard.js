const API_BASE = 'http://localhost:5000/api';

let charts = {};

const COLORS = {
    mint: '#7dd3c0',
    teal: '#5fb9a9',
    cyan: '#4ba8bc',
    green: '#10b981',
    blue: '#3b82f6',
    purple: '#8b5cf6',
    pink: '#ec4899',
    orange: '#f59e0b'
};

Chart.defaults.color = '#a0aec0';
Chart.defaults.borderColor = '#1f2937';
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif';

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching metrics:', error);
        document.querySelector('.dashboard-content').innerHTML = `
            <div class="loading">
                <div>
                    <h2 style="color: #7dd3c0; margin-bottom: 16px;">Error loading dashboard</h2>
                    <p style="color: #6b7280;">${error.message}</p>
                    <p style="color: #6b7280; margin-top: 8px;">Make sure the API server is running on port 5000</p>
                </div>
            </div>
        `;
        throw error;
    }
}

function updateStatCards(data) {
    document.getElementById('total-users').textContent = data.users?.total_users || '-';

    const dauValues = Object.values(data.sessions?.dau_by_date || {});
    const latestDAU = dauValues[dauValues.length - 1] || '-';
    document.getElementById('dau').textContent = latestDAU;

    const vibeValues = Object.values(data.vibes?.vibes_by_date || {});
    const latestVibes = vibeValues[vibeValues.length - 1] || '-';
    document.getElementById('total-vibes').textContent = latestVibes;

    document.getElementById('match-rate').textContent = `${(data.matches?.vibe_to_match_rate || 0).toFixed(1)}%`;

    const premiumUsers = data.users?.premium_users || '-';
    document.getElementById('premium-users').textContent = premiumUsers;

    const messageValues = Object.values(data.messages?.messages_by_date || {});
    const latestMessages = messageValues[messageValues.length - 1] || '-';
    document.getElementById('messages-today').textContent = latestMessages;

    document.getElementById('response-rate').textContent = `${(data.messages?.response_rate || 0).toFixed(1)}%`;

    const totalUsers = data.users?.total_users || 0;
    const signupDates = Object.keys(data.users?.signups_by_date || {}).sort();
    if (signupDates.length >= 2) {
        const recent = data.users.signups_by_date[signupDates[signupDates.length - 1]] || 0;
        const previous = data.users.signups_by_date[signupDates[signupDates.length - 2]] || 1;
        const growth = previous > 0 ? ((recent / previous - 1) * 100).toFixed(1) : '0.0';
        document.getElementById('weekly-growth').textContent = `${growth}%`;
    } else {
        document.getElementById('weekly-growth').textContent = '0%';
    }
}

function createEngagementChart(data) {
    const ctx = document.getElementById('engagement-chart');
    if (!ctx) return;

    if (charts['engagement-chart']) {
        charts['engagement-chart'].destroy();
    }

    const dates = Object.keys(data.vibes?.vibes_by_date || {}).sort();
    const vibeValues = dates.map(date => data.vibes.vibes_by_date[date]);
    const matchValues = dates.map(date => data.matches.matches_by_date?.[date] || 0);
    const messageValues = dates.map(date => data.messages.messages_by_date?.[date] || 0);

    charts['engagement-chart'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Vibes',
                    data: vibeValues,
                    borderColor: COLORS.mint,
                    backgroundColor: COLORS.mint + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Matches',
                    data: matchValues,
                    borderColor: COLORS.cyan,
                    backgroundColor: COLORS.cyan + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Messages',
                    data: messageValues,
                    borderColor: COLORS.teal,
                    backgroundColor: COLORS.teal + '20',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#141923',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    padding: 12,
                    bodySpacing: 6,
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1f2937',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                }
            }
        }
    });
}

function createFunnel(data) {
    const container = document.getElementById('funnel-container');
    if (!container) return;

    const funnel = data.funnel;
    if (!funnel) return;

    const stages = [
        { label: 'Signups', value: funnel.signups, percentage: 100 },
        { label: 'Profile Complete', value: funnel.profile_complete, percentage: (funnel.profile_complete / funnel.signups * 100) },
        { label: 'First Vibe Sent', value: funnel.first_vibe_sent, percentage: (funnel.first_vibe_sent / funnel.signups * 100) },
        { label: 'Match Created', value: funnel.match_created, percentage: (funnel.match_created / funnel.signups * 100) },
        { label: 'First Message', value: funnel.first_message, percentage: (funnel.first_message / funnel.signups * 100) }
    ];

    container.innerHTML = stages.map(stage => `
        <div class="funnel-stage">
            <div class="funnel-bar-container">
                <div class="funnel-bar" style="width: ${stage.percentage}%">
                    <span class="funnel-label">${stage.label}</span>
                    <span class="funnel-value">${stage.value}</span>
                </div>
            </div>
            <div class="funnel-percentage">${stage.percentage.toFixed(1)}%</div>
        </div>
    `).join('');
}

function createLineChart(canvasId, label, dates, values, color = COLORS.mint) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

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
                fill: true,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#141923',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    padding: 12,
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1f2937',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                }
            }
        }
    });
}

function createBarChart(canvasId, label, labels, values, color = COLORS.mint) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

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
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#141923',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    padding: 12,
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1f2937',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                }
            }
        }
    });
}

function createDoughnutChart(canvasId, labels, values, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0aec0',
                        padding: 16,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#141923',
                    borderColor: '#1f2937',
                    borderWidth: 1,
                    padding: 12,
                    titleColor: '#ffffff',
                    bodyColor: '#a0aec0'
                }
            }
        }
    });
}

function updateCharts(data) {
    createEngagementChart(data);
    createFunnel(data);

    const dauDates = Object.keys(data.sessions?.dau_by_date || {}).sort();
    const dauValues = dauDates.map(date => data.sessions.dau_by_date[date]);
    createLineChart('dau-chart', 'Daily Active Users', dauDates, dauValues, COLORS.mint);

    const sessionDates = Object.keys(data.sessions?.sessions_by_date || {}).sort();
    const sessionValues = sessionDates.map(date => data.sessions.sessions_by_date[date]);
    createLineChart('sessions-chart', 'Sessions', sessionDates, sessionValues, COLORS.teal);

    const activityHours = Object.keys(data.activity?.activity_by_hour || {}).sort((a, b) => parseInt(a) - parseInt(b));
    const activityValues = activityHours.map(hour => data.activity.activity_by_hour[hour]);
    createBarChart('activity-chart', 'Activity', activityHours.map(h => `${h}:00`), activityValues, COLORS.cyan);

    const adjLabels = Object.keys(data.vibes?.vibes_by_adjective || {}).slice(0, 8);
    const adjValues = adjLabels.map(adj => data.vibes.vibes_by_adjective[adj]);
    createBarChart('adjectives-chart', 'Count', adjLabels, adjValues, COLORS.mint);

    const depthLabels = Object.keys(data.conversations?.depth_distribution || {});
    const depthValues = Object.values(data.conversations?.depth_distribution || {});
    createBarChart('conversation-depth-chart', 'Conversations', depthLabels, depthValues, COLORS.teal);

    const genderLabels = Object.keys(data.demographics?.gender || {});
    const genderValues = Object.values(data.demographics?.gender || {});
    createDoughnutChart('gender-chart', genderLabels, genderValues, [COLORS.mint, COLORS.cyan]);
}

async function initDashboard() {
    try {
        const data = await fetchMetrics();
        updateStatCards(data);
        updateCharts(data);

        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('update-time').textContent = `just now`;
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
}

document.addEventListener('DOMContentLoaded', initDashboard);

setInterval(initDashboard, 30000);
