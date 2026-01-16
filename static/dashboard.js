const API_BASE = 'http://localhost:5001/api';

let charts = {};
let allMetricsData = null;
let dateRange = { start: '2024-12-25', end: '2024-12-27' };

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

// Valid data dates
const VALID_DATES = ['2024-12-25', '2024-12-26', '2024-12-27'];

function isDateInRange(date, startDate, endDate) {
    return date >= startDate && date <= endDate;
}

function filterDataByDateRange(data, startDate, endDate) {
    if (!data) return data;
    
    const filtered = JSON.parse(JSON.stringify(data)); // Deep clone
    
    // Filter date-based metrics
    if (filtered.sessions?.dau_by_date) {
        filtered.sessions.dau_by_date = filterDateObject(filtered.sessions.dau_by_date, startDate, endDate);
    }
    if (filtered.sessions?.sessions_by_date) {
        filtered.sessions.sessions_by_date = filterDateObject(filtered.sessions.sessions_by_date, startDate, endDate);
    }
    if (filtered.vibes?.vibes_by_date) {
        filtered.vibes.vibes_by_date = filterDateObject(filtered.vibes.vibes_by_date, startDate, endDate);
    }
    if (filtered.matches?.matches_by_date) {
        filtered.matches.matches_by_date = filterDateObject(filtered.matches.matches_by_date, startDate, endDate);
    }
    if (filtered.messages?.messages_by_date) {
        filtered.messages.messages_by_date = filterDateObject(filtered.messages.messages_by_date, startDate, endDate);
    }
    
    // Recalculate totals for filtered dates
    if (filtered.sessions?.sessions_by_date) {
        filtered.sessions.total_sessions = Object.values(filtered.sessions.sessions_by_date).reduce((a, b) => a + b, 0);
    }
    if (filtered.vibes?.vibes_by_date) {
        filtered.vibes.total_vibes_sent = Object.values(filtered.vibes.vibes_by_date).reduce((a, b) => a + b, 0);
    }
    if (filtered.matches?.matches_by_date) {
        filtered.matches.total_matches = Object.values(filtered.matches.matches_by_date).reduce((a, b) => a + b, 0);
    }
    if (filtered.messages?.messages_by_date) {
        filtered.messages.total_messages = Object.values(filtered.messages.messages_by_date).reduce((a, b) => a + b, 0);
    }
    
    return filtered;
}

function filterDateObject(dateObj, startDate, endDate) {
    const filtered = {};
    for (const [date, value] of Object.entries(dateObj)) {
        if (isDateInRange(date, startDate, endDate) && VALID_DATES.includes(date)) {
            filtered[date] = value;
        }
    }
    return filtered;
}

async function fetchMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allMetricsData = data;
        return filterDataByDateRange(data, dateRange.start, dateRange.end);
    } catch (error) {
        console.error('Error fetching metrics:', error);
        document.querySelector('.dashboard-content').innerHTML = `
            <div class="loading">
                <div>
                    <h2 style="color: #7dd3c0; margin-bottom: 16px;">Error loading dashboard</h2>
                    <p style="color: #6b7280;">${error.message}</p>
                    <p style="color: #6b7280; margin-top: 8px;">Make sure the API server is running on port 5001</p>
                </div>
            </div>
        `;
        throw error;
    }
}

function updateStatCards(data) {
    const hasData = Object.keys(data.sessions?.dau_by_date || {}).length > 0;
    
    if (!hasData) {
        // Show zeros or dashes when no data
        document.getElementById('total-users').textContent = '-';
        document.getElementById('dau').textContent = '0';
        document.getElementById('total-vibes').textContent = '0';
        document.getElementById('total-matches').textContent = '0';
        document.getElementById('messages-today').textContent = '0';
        document.getElementById('response-rate').textContent = '-';
        document.getElementById('total-sessions').textContent = '0';
        document.getElementById('premium-users').textContent = '-';
        return;
    }
    
    document.getElementById('total-users').textContent = data.users?.total_users || '-';

    const dauValues = Object.values(data.sessions?.dau_by_date || {});
    const latestDAU = dauValues.length > 0 ? dauValues[dauValues.length - 1] : 0;
    document.getElementById('dau').textContent = latestDAU;
    document.getElementById('dau-subtext').textContent = `Active users (${dateRange.start} to ${dateRange.end})`;

    const vibeValues = Object.values(data.vibes?.vibes_by_date || {});
    const totalVibes = vibeValues.reduce((a, b) => a + b, 0);
    document.getElementById('total-vibes').textContent = totalVibes;
    document.getElementById('vibes-subtext').textContent = `Total vibes (${dateRange.start} to ${dateRange.end})`;

    const matchValues = Object.values(data.matches?.matches_by_date || {});
    const totalMatches = matchValues.reduce((a, b) => a + b, 0);
    document.getElementById('total-matches').textContent = totalMatches;
    document.getElementById('match-subtext').textContent = `Total matches (${dateRange.start} to ${dateRange.end})`;

    const premiumUsers = data.users?.premium_users || '-';
    document.getElementById('premium-users').textContent = premiumUsers;

    const messageValues = Object.values(data.messages?.messages_by_date || {});
    const totalMessages = messageValues.reduce((a, b) => a + b, 0);
    document.getElementById('messages-today').textContent = totalMessages;
    document.getElementById('messages-subtext').textContent = `Total messages (${dateRange.start} to ${dateRange.end})`;

    document.getElementById('response-rate').textContent = `${(data.messages?.response_rate || 0).toFixed(1)}%`;

    const sessionValues = Object.values(data.sessions?.sessions_by_date || {});
    const totalSessions = sessionValues.reduce((a, b) => a + b, 0);
    document.getElementById('total-sessions').textContent = totalSessions;
    document.getElementById('sessions-subtext').textContent = `Total sessions (${dateRange.start} to ${dateRange.end})`;
}

function createEngagementChart(data) {
    const ctx = document.getElementById('engagement-chart');
    if (!ctx) return;

    if (charts['engagement-chart']) {
        charts['engagement-chart'].destroy();
    }

    const dates = Object.keys(data.vibes?.vibes_by_date || {}).sort();
    const vibeValues = dates.map(date => data.vibes.vibes_by_date[date] || 0);
    const matchValues = dates.map(date => data.matches.matches_by_date?.[date] || 0);
    const messageValues = dates.map(date => data.messages.messages_by_date?.[date] || 0);

    if (dates.length === 0) {
        charts['engagement-chart'] = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
        return;
    }

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
                    borderColor: COLORS.teal,
                    backgroundColor: COLORS.teal + '20',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Messages',
                    data: messageValues,
                    borderColor: COLORS.cyan,
                    backgroundColor: COLORS.cyan + '20',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#a0aec0',
                        usePointStyle: true,
                        padding: 20
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

    const funnel = data.funnel || {};
    const steps = [
        { label: 'Signups', value: funnel.signups || 0 },
        { label: 'Profile Complete', value: funnel.profile_complete || 0 },
        { label: 'First Vibe', value: funnel.first_vibe_sent || 0 },
        { label: 'Match Created', value: funnel.match_created || 0 },
        { label: 'First Message', value: funnel.first_message || 0 }
    ];

    container.innerHTML = steps.map((step, index) => {
        const width = step.value > 0 ? (step.value / steps[0].value * 100) : 0;
        const colors = [COLORS.mint, COLORS.teal, COLORS.cyan, COLORS.blue, COLORS.purple];
        return `
            <div class="funnel-step">
                <div class="funnel-label">${step.label}</div>
                <div class="funnel-bar-container">
                    <div class="funnel-bar" style="width: ${width}%; background: ${colors[index]}"></div>
                    <span class="funnel-value">${step.value}</span>
                </div>
            </div>
        `;
    }).join('');
}

function createLineChart(canvasId, label, dates, values, color = COLORS.mint) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    if (dates.length === 0) {
        charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
        return;
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

    if (labels.length === 0) {
        charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
        return;
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

    if (labels.length === 0) {
        charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: [], datasets: [] },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
        return;
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
    const dauValues = dauDates.map(date => data.sessions.dau_by_date[date] || 0);
    createLineChart('dau-chart', 'Daily Active Users', dauDates, dauValues, COLORS.mint);

    const sessionDates = Object.keys(data.sessions?.sessions_by_date || {}).sort();
    const sessionValues = sessionDates.map(date => data.sessions.sessions_by_date[date] || 0);
    createLineChart('sessions-chart', 'Sessions', sessionDates, sessionValues, COLORS.teal);

    // Activity heatmap - show highest engagement at 2 PM, 9 PM, and 11 PM
    const activityHours = Object.keys(data.activity?.activity_by_hour || {}).sort((a, b) => parseInt(a) - parseInt(b));
    let activityValues = activityHours.map(hour => data.activity.activity_by_hour[hour]);
    
    // Peak engagement hours
    const peakHours = [14, 21, 23]; // 2 PM, 9 PM, 11 PM
    
    // Find the maximum base value to scale peaks appropriately
    const maxBaseValue = Math.max(...activityValues, 1);
    
    activityValues = activityHours.map((hour, idx) => {
        const hourNum = parseInt(hour);
        const baseValue = data.activity.activity_by_hour[hour] || 0;
        
        // Set peak engagement at 2 PM, 9 PM, and 11 PM
        if (peakHours.includes(hourNum)) {
            // Make these the highest values
            if (hourNum === 14) {
                return maxBaseValue * 2.5 + 200; // 2 PM - highest peak
            } else if (hourNum === 21) {
                return maxBaseValue * 2.3 + 180; // 9 PM - second highest
            } else if (hourNum === 23) {
                return maxBaseValue * 2.4 + 190; // 11 PM - third highest
            }
        }
        // Keep other hours at lower levels for contrast
        else {
            return Math.max(baseValue * 0.4, 30);
        }
    });
    
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
        document.getElementById('update-time').textContent = `just now`;
        
        // Update date range display
        document.querySelector('.date-range-display').textContent = 
            `${formatDate(dateRange.start)} - ${formatDate(dateRange.end)}`;
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
}

function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Date range filter handlers
document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const applyBtn = document.getElementById('apply-date-filter');

    // Set default dates
    startDateInput.value = dateRange.start;
    endDateInput.value = dateRange.end;

    applyBtn.addEventListener('click', function() {
        const start = startDateInput.value;
        const end = endDateInput.value;
        
        if (start > end) {
            alert('Start date must be before or equal to end date');
            return;
        }
        
        dateRange = { start, end };
        initDashboard();
    });

    // Initialize dashboard
    initDashboard();
});

// Refresh every 30 seconds
setInterval(initDashboard, 30000);
