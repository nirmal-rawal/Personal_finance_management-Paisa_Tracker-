document.addEventListener("DOMContentLoaded", function () {
    // Income vs Expenses Chart (Bar Chart)
    const incomeExpenseCtx = document.getElementById('incomeExpenseChart').getContext('2d');
    const incomeExpenseChart = new Chart(incomeExpenseCtx, {
        type: 'bar',
        data: {
            labels: chartData.chartLabels,
            datasets: [
                {
                    label: 'Income',
                    data: chartData.chartIncomeData,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                },
                {
                    label: 'Expenses',
                    data: chartData.chartExpenseData,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${chartData.currencySymbol}${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return chartData.currencySymbol + value;
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Expense Breakdown Chart (Doughnut Chart)
const expenseBreakdownCtx = document.getElementById('expenseBreakdownChart').getContext('2d');
const expenseBreakdownChart = new Chart(expenseBreakdownCtx, {
    type: 'doughnut',
    data: {
        labels: chartData.expenseBreakdownLabels,
        datasets: [{
            data: chartData.expenseBreakdownValues,
            backgroundColor: [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)'
            ].slice(0, chartData.expenseBreakdownLabels.length),
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    font: {
                        size: 12
                    },
                    padding: 20
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: ${chartData.currencySymbol}${(value * total_expenses / 100).toFixed(2)} (${percentage}%)`;
                    }
                }
            },
            datalabels: {
                formatter: (value) => {
                    return Math.round(value) + '%';
                },
                color: '#fff',
                font: {
                    weight: 'bold'
                }
            }
        },
        cutout: '70%'
    },
    plugins: [ChartDataLabels]
});

    // Cash Flow Summary Chart (Line Chart)
    const cashFlowCtx = document.getElementById('cashFlowChart').getContext('2d');
    const cashFlowChart = new Chart(cashFlowCtx, {
        type: 'line',
        data: {
            labels: chartData.chartLabels,
            datasets: [{
                label: 'Net Savings',
                data: chartData.netSavingsTrend,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Net Savings: ${chartData.currencySymbol}${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return chartData.currencySymbol + value;
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Budget progress bar color update
    const progressBar = document.querySelector('.progress-bar');
    if (chartData.budgetPercentage > 100) {
        progressBar.classList.add('bg-danger');
    } else if (chartData.budgetPercentage > 80) {
        progressBar.classList.add('bg-warning');
    } else {
        progressBar.classList.add('bg-success');
    }
    
});
// Add hover effects to transaction rows
document.querySelectorAll('.recent-transactions-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', function() {
        this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
    });
    row.addEventListener('mouseleave', function() {
        this.style.boxShadow = 'none';
    });
});