/* ============================================
   Dashboard Page JavaScript
   Uses server-injected data — NO fetch needed!
   ============================================ */

let forecastChartInstance = null;

/**
 * On page load, use the data injected by the backend
 */
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

/**
 * Load dashboard using server-injected data (window.__FORECAST_DATA__)
 */
function loadDashboard() {
    setStatus('Loading...', 'loading');

    try {
        const data = window.__FORECAST_DATA__;

        if (!data || !data.forecast) {
            throw new Error('Forecast data not available. Try refreshing the page.');
        }

        console.log('Forecast data loaded:', data);

        // Populate the dashboard
        populateKPIs(data);
        renderChart(data.forecast);
        setStatus('Forecast Ready', 'ready');

    } catch (error) {
        console.error('Dashboard Error:', error);
        setStatus('Error', 'error');
        showToast(`Dashboard error: ${error.message}`);
    }
}

/**
 * Populate KPI cards with data
 */
function populateKPIs(data) {
    const { summary, forecast } = data;

    // Find peak day
    const peakDay = forecast.reduce((max, item) =>
        item.predicted_sales > max.predicted_sales ? item : max
    );

    // Total Sales
    const totalEl = document.getElementById('totalSales');
    animateValue(totalEl, summary.total_predicted_sales, true);
    animateBar('.kpi-bar-blue', 85);

    // Average Sales
    const avgEl = document.getElementById('avgSales');
    animateValue(avgEl, summary.avg_predicted_sales, true);
    animateBar('.kpi-bar-purple', 65);

    // Forecast Days
    const daysEl = document.getElementById('forecastDays');
    daysEl.innerHTML = `<strong>${summary.forecast_days}</strong> days`;
    animateBar('.kpi-bar-emerald', 100);

    // Peak Sales
    const peakEl = document.getElementById('peakSales');
    animateValue(peakEl, peakDay.predicted_sales, true);
    document.getElementById('peakDate').textContent = formatDate(peakDay.date);
    animateBar('.kpi-bar-amber', 75);
}

/**
 * Animate a number counting up
 */
function animateValue(element, target, isCurrency) {
    const duration = 1400;
    const start = performance.now();

    function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const current = target * ease;

        element.textContent = isCurrency ? formatCurrency(current) : Math.round(current).toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(tick);
        }
    }

    requestAnimationFrame(tick);
}

/**
 * Animate KPI bar fill
 */
function animateBar(selector, percent) {
    setTimeout(() => {
        const bar = document.querySelector(selector);
        if (bar) bar.style.width = percent + '%';
    }, 300);
}

/**
 * Format number as currency
 */
function formatCurrency(value) {
    if (value >= 1_000_000) {
        return '$' + (value / 1_000_000).toFixed(2) + 'M';
    }
    if (value >= 1_000) {
        return '$' + (value / 1_000).toFixed(1) + 'K';
    }
    return '$' + Math.round(value).toLocaleString();
}

/**
 * Format date string nicely
 */
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Render the forecast chart with Chart.js
 */
function renderChart(forecastData) {
    const ctx = document.getElementById('forecastChart').getContext('2d');

    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    const labels = forecastData.map(item => {
        const d = new Date(item.date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const values = forecastData.map(item => item.predicted_sales);

    // Gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, 360);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
    gradient.addColorStop(0.6, 'rgba(139, 92, 246, 0.08)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Sales ($)',
                data: values,
                fill: true,
                backgroundColor: gradient,
                borderColor: '#3b82f6',
                borderWidth: 2.5,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#111a2e',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                pointHoverBackgroundColor: '#60a5fa',
                pointHoverBorderColor: '#ffffff',
                pointHoverBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        color: '#8b95b0',
                        font: { family: "'Inter', sans-serif", size: 12, weight: '600' },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                    }
                },
                tooltip: {
                    backgroundColor: '#111a2e',
                    titleColor: '#edf0f7',
                    bodyColor: '#8b95b0',
                    borderColor: 'rgba(255,255,255,0.08)',
                    borderWidth: 1,
                    padding: 14,
                    cornerRadius: 10,
                    titleFont: { family: "'Inter', sans-serif", size: 13, weight: '700' },
                    bodyFont: { family: "'Inter', sans-serif", size: 12 },
                    displayColors: false,
                    callbacks: {
                        label: function (ctx) {
                            return 'Sales: $' + ctx.raw.toLocaleString(undefined, { maximumFractionDigits: 0 });
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
                    ticks: {
                        color: '#5a6484',
                        font: { family: "'Inter', sans-serif", size: 11 },
                        maxRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 15,
                    },
                    border: { display: false }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.03)', drawBorder: false },
                    ticks: {
                        color: '#5a6484',
                        font: { family: "'Inter', sans-serif", size: 11 },
                        callback: (v) => '$' + (v / 1000).toFixed(0) + 'K',
                        padding: 8,
                    },
                    border: { display: false }
                }
            }
        }
    });

    // Hide loading overlay
    document.getElementById('chartLoading').classList.add('hidden');
}

/**
 * Update sidebar status indicator
 */
function setStatus(text, state) {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusText');

    label.textContent = text;
    dot.className = 'status-dot';
    if (state === 'ready') dot.classList.add('ready');
    else if (state === 'error') dot.classList.add('error');
}

/**
 * Toggle sidebar on mobile
 */
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

/**
 * Show error toast
 */
function showToast(message) {
    const toast = document.getElementById('toast');
    document.getElementById('toastMessage').textContent = message;
    toast.classList.add('show');

    setTimeout(() => toast.classList.remove('show'), 6000);
}

/**
 * Hide toast
 */
function hideToast() {
    document.getElementById('toast').classList.remove('show');
}
