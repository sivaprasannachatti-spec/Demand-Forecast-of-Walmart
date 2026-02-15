/* ============================================
   Walmart Demand Forecasting Dashboard
   JavaScript - API Calls, Charts, Interactions
   ============================================ */

const API_BASE = '/api/v1';
let forecastChartInstance = null;

/**
 * Fetch predictions from the backend API
 */
async function fetchPredictions() {
    const btn = document.getElementById('predictBtn');
    const loader = document.getElementById('btnLoader');

    // Show loading state
    btn.classList.add('loading');
    updateNavStatus('Generating Forecast...', false);

    try {
        const response = await fetch(`${API_BASE}/predict_sales`);

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        const data = result.data;

        if (!data || !data.forecast) {
            throw new Error('Invalid response format');
        }

        // Populate dashboard
        populateKPIs(data);
        renderForecastChart(data.forecast);

        // Transition to dashboard
        showDashboard();
        updateNavStatus('Forecast Ready', true);

    } catch (error) {
        console.error('Forecast Error:', error);
        showToast(error.message || 'Failed to generate forecast. Make sure the server is running.');
        updateNavStatus('Error', false);
    } finally {
        btn.classList.remove('loading');
    }
}

/**
 * Populate KPI cards with forecast data
 */
function populateKPIs(data) {
    const summary = data.summary;
    const forecast = data.forecast;

    // Total Sales
    const totalEl = document.getElementById('totalSales');
    animateNumber(totalEl, summary.total_predicted_sales, true);

    // Average Sales
    const avgEl = document.getElementById('avgSales');
    animateNumber(avgEl, summary.avg_predicted_sales, true);

    // Forecast Days
    const daysEl = document.getElementById('forecastDays');
    daysEl.textContent = `${summary.forecast_days} days`;

    // Peak Sales Day
    const peakDay = forecast.reduce((max, item) => 
        item.predicted_sales > max.predicted_sales ? item : max
    );
    const peakEl = document.getElementById('peakSales');
    animateNumber(peakEl, peakDay.predicted_sales, true);

    const peakDateEl = document.getElementById('peakDate');
    peakDateEl.textContent = formatDate(peakDay.date);
}

/**
 * Animate number counting up
 */
function animateNumber(el, target, isCurrency) {
    const duration = 1200;
    const startTime = performance.now();
    const start = 0;

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const ease = 1 - Math.pow(1 - progress, 3);
        const current = start + (target - start) * ease;

        el.textContent = isCurrency ? formatCurrency(current) : Math.round(current).toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Format number as currency
 */
function formatCurrency(value) {
    if (value >= 1000000) {
        return `$${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
        return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
}

/**
 * Format date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Render the forecast chart using Chart.js
 */
function renderForecastChart(forecastData) {
    const ctx = document.getElementById('forecastChart').getContext('2d');

    // Destroy previous chart if exists
    if (forecastChartInstance) {
        forecastChartInstance.destroy();
    }

    const labels = forecastData.map(item => {
        const d = new Date(item.date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const values = forecastData.map(item => item.predicted_sales);

    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 380);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
    gradient.addColorStop(0.5, 'rgba(139, 92, 246, 0.10)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    forecastChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Predicted Sales',
                data: values,
                fill: true,
                backgroundColor: gradient,
                borderColor: '#3b82f6',
                borderWidth: 2.5,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#1a1f35',
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
                        color: '#9ca3be',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12,
                            weight: '600'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1f35',
                    titleColor: '#f0f2f8',
                    bodyColor: '#9ca3be',
                    borderColor: 'rgba(255,255,255,0.08)',
                    borderWidth: 1,
                    padding: 14,
                    titleFont: {
                        family: "'Inter', sans-serif",
                        size: 13,
                        weight: '700'
                    },
                    bodyFont: {
                        family: "'Inter', sans-serif",
                        size: 12,
                    },
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Sales: $${context.raw.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.04)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#6b7493',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11,
                        },
                        maxRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 15,
                    },
                    border: { display: false }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.04)',
                        drawBorder: false,
                    },
                    ticks: {
                        color: '#6b7493',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11,
                        },
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        },
                        padding: 8
                    },
                    border: { display: false }
                }
            }
        }
    });
}

/**
 * Show the dashboard section and hide the landing
 */
function showDashboard() {
    document.getElementById('landingSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Go back to the landing page
 */
function goBack() {
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('landingSection').style.display = 'flex';
    updateNavStatus('System Ready', true);
}

/**
 * Update navbar status indicator
 */
function updateNavStatus(text, isHealthy) {
    const statusText = document.querySelector('.status-text');
    const statusDot = document.querySelector('.status-dot');

    statusText.textContent = text;
    statusDot.style.background = isHealthy ? '#10b981' : '#f59e0b';
}

/**
 * Show toast notification
 */
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMessage');
    toastMsg.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}
