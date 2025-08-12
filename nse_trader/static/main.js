let accuracyGaugeChart;
let riskRewardChart;
let currentSymbol = null;

// Fetch available stocks for the dropdown
fetch('/api/stocks/list')
    .then(response => response.json())
    .then(stocks => {
        const dropdown = document.getElementById('stock-dropdown');
        stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.symbol;
            option.textContent = stock.name;
            dropdown.appendChild(option);
        });

        // Initialize with first stock in the list
        if (stocks.length > 0) {
            currentSymbol = stocks[0].symbol;
            createTradingViewWidget(currentSymbol);
            fetchAnalysis(currentSymbol);
        }
    })
    .catch(error => {
        console.error('Error fetching stock list:', error);
        showError('Failed to load stock list. Please try again later.');

        // Initialize with default symbol even on error
        currentSymbol = 'DANGCEM';
        createTradingViewWidget(currentSymbol);
    });

document.getElementById('stock-dropdown').addEventListener('change', function() {
    const symbol = this.value;
    currentSymbol = symbol;

    // Update the TradingView widget with the new symbol
    createTradingViewWidget(symbol);

    // Still fetch analysis and entry/exit points from our API
    fetchStockDetails(symbol);
    fetchAnalysis(symbol);
});

function fetchStockDetails(symbol) {
    showLoading('stock-details');
    fetch(`/api/stock/${symbol}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading('stock-details');
            const stockDetails = document.getElementById('stock-details');
            stockDetails.innerHTML = `
                <div class="col-md-12 mb-4">
                    <div class="card stock-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h5 class="card-title mb-0">${data.symbol}</h5>
                                    <h6 class="card-subtitle text-muted">${data.name}</h6>
                                </div>
                            </div>

                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <p class="card-text mb-0 h4">${data.price}</p>
                                    <p class="card-text ${data.change > 0 ? 'text-success' : 'text-danger'} mb-0">
                                        ${data.change_percent}
                                    </p>
                                </div>
                                <div class="text-end">
                                    <div class="text-muted small">Market Cap</div>
                                    <div class="fw-bold">${data.market_cap}</div>
                                </div>
                            </div>

                            <div class="row mb-3">
                                <div class="col">
                                    <div class="text-muted small">Volume</div>
                                    <div>${data.volume}</div>
                                </div>
                                <div class="col text-end">
                                    <div class="text-muted small">Value</div>
                                    <div>${data.value}</div>
                                </div>
                            </div>

                            <div class="trading-info">
                                <div class="d-flex justify-content-between mb-2">
                                    <small class="text-muted">Open</small>
                                    <span>${data.open}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-2">
                                    <small class="text-muted">High</small>
                                    <span>${data.high}</span>
                                </div>
                                <div class="d-flex justify-content-between mb-3">
                                    <small class="text-muted">Low</small>
                                    <span>${data.low}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            hideLoading('stock-details');
            console.error('Error fetching stock details:', error);
            showError(`Failed to load stock details for ${symbol}.`);
        });
}


function fetchAnalysis(symbol) {
    showLoading('analysis');
    fetch(`/api/analysis/${symbol}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideLoading('analysis');

            // Update analysis text
            document.getElementById('analysis-text').textContent = data.recommendation || 'No explanation available.';

            // Update recommendation badge
            const recommendationBadge = document.getElementById('recommendation-badge');
            recommendationBadge.textContent = data.recommendation?.toUpperCase() || 'NEUTRAL';
            recommendationBadge.className = `badge ${getRecommendationClass(data.recommendation)}`;

            // Update entry, stop loss, and take profit values
            document.getElementById('entry-price').textContent = formatCurrency(data.price);
            document.getElementById('risk-value').textContent = formatCurrency(data.stop_loss);
            document.getElementById('reward-value').textContent = formatCurrency(data.take_profit);

            // Update reason list
            const reasonList = document.getElementById('reason-list');
            reasonList.innerHTML = '';

            const indicators = data.indicators;
            if (indicators) {
                const reasons = [
                    `RSI: ${indicators.rsi.toFixed(2)}`,
                    `MACD Signal: ${indicators.macd}`,
                    `Bollinger Signal: ${indicators.bollinger}`,
                    `Momentum: ${indicators.momentum.toFixed(2)}`
                ];
                reasons.forEach(reason => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.innerHTML = `<i class="bi bi-check-circle me-2"></i>${reason}`;
                    reasonList.appendChild(li);
                });
            }

            // Update accuracy gauge (simulate historical accuracy)
            const accuracy = Math.round(65 + Math.random() * 20); // Simulate 65-85% accuracy
            updateAccuracyGauge(accuracy);

            // Update risk/reward chart
            updateRiskRewardChart(data.price, data.stop_loss, data.take_profit);
        })
        .catch(error => {
            hideLoading('analysis');
            console.error('Error fetching analysis:', error);
            showError(`Failed to load analysis for ${symbol}.`);
        });
}

function updateAccuracyGauge(accuracy) {
    document.getElementById('accuracy-percentage').textContent = `${accuracy}%`;

    if (accuracyGaugeChart) {
        accuracyGaugeChart.destroy();
    }

    const ctx = document.getElementById('accuracyGauge').getContext('2d');
    accuracyGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [accuracy, 100-accuracy],
                backgroundColor: [
                    accuracy >= 70 ? '#4CAF50' : accuracy >= 50 ? '#FFC107' : '#F44336',
                    '#E0E0E0'
                ],
                borderWidth: 0
            }]
        },
        options: {
            circumference: 180,
            rotation: 270,
            cutout: '70%',
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function updateRiskRewardChart(entry, stopLoss, takeProfit) {
    const risk = entry - stopLoss;
    const reward = takeProfit - entry;
    const ratio = (reward / risk).toFixed(1);

    if (riskRewardChart) {
        riskRewardChart.destroy();
    }

    const ctx = document.getElementById('riskRewardChart').getContext('2d');
    riskRewardChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Risk', 'Reward'],
            datasets: [{
                data: [risk, reward],
                backgroundColor: ['#F44336', '#4CAF50'],
                barThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const value = context.raw;
                            return context.dataIndex === 0
                                ? `Risk: ${formatCurrency(value)}`
                                : `Reward: ${formatCurrency(value)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount (₦)'
                    }
                }
            }
        }
    });

    // Add ratio text
    const canvas = document.getElementById('riskRewardChart');
    const centerX = canvas.width / 2;
    const topY = 30;

    setTimeout(() => {
        const ctx = canvas.getContext('2d');
        ctx.save();
        ctx.textAlign = 'center';
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(`1:${ratio} Ratio`, centerX, topY);
        ctx.restore();
    }, 100);
}

function formatCurrency(value) {
    // Format as Nigerian Naira
    return new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'NGN',
        minimumFractionDigits: 2
    }).format(value);
}

function showLoading(sectionId) {
    // Could implement a loading indicator for each section
    console.log(`Loading ${sectionId}...`);
}

function hideLoading(sectionId) {
    // Hide the loading indicator
    console.log(`Finished loading ${sectionId}`);
}

function showError(message) {
    // Could implement a toast notification
    console.error(message);
}

function getRecommendationClass(recommendation) {
    switch (recommendation?.toUpperCase()) {
        case 'STRONG_BUY':
        case 'BUY': return 'badge-buy';
        case 'STRONG_SELL':
        case 'SELL': return 'badge-sell';
        default: return 'badge-neutral';
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-NG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// Helper function to get recommendation alert class
function getRecommendationAlertClass(recommendation) {
    switch (recommendation?.toUpperCase()) {
        case 'STRONG_BUY':
        case 'BUY': return 'alert-success';
        case 'STRONG_SELL':
        case 'SELL': return 'alert-danger';
        default: return 'alert-secondary';
    }
}

// Fetch market summary
async function fetchMarketSummary() {
    showLoading('market-summary');
    try {
        const response = await fetch('/api/market-summary');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();

        document.getElementById('asi-value').textContent = data.asi;

        const asiChange = document.getElementById('asi-change');
        asiChange.textContent = data.change_percent;
        asiChange.className = data.change > 0 ? 'card-text text-success' : 'card-text text-danger';

        document.getElementById('market-cap').textContent = data.market_cap;
        document.getElementById('volume').textContent = data.volume;
        document.getElementById('value').textContent = data.value;

        if (data.last_update) {
            document.getElementById('last-update').textContent =
                'Last update: ' + formatDate(data.last_update);
        }

        hideLoading('market-summary');
    } catch (error) {
        hideLoading('market-summary');
        console.error('Error fetching market summary:', error);
        showError('Failed to load market summary data');
    }
}

// Update data every minute
function startDataUpdates() {
    fetchMarketSummary();

    setInterval(() => {
        fetchMarketSummary();

        // If a stock is currently selected, refresh its data too
        if (currentSymbol) {
            fetchStockDetails(currentSymbol);
            fetchAnalysis(currentSymbol);
        }
    }, 60000);
}

// Start updates when page loads
document.addEventListener('DOMContentLoaded', startDataUpdates);
