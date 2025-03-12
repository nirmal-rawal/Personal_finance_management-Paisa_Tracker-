document.addEventListener("DOMContentLoaded", function () {
    // Income vs Expenses Chart
    const ctx1 = document.getElementById('incomeExpenseChart').getContext('2d');
    const incomeExpenseChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: chartData.chartLabels,
            datasets: [
                {
                    label: 'Income',
                    data: chartData.chartIncomeData,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                },
                {
                    label: 'Expenses',
                    data: chartData.chartExpenseData,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true, // Ensure the chart is responsive
            maintainAspectRatio: false, // Disable aspect ratio maintenance
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                        color: 'white',
                    },
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                        color: 'white',
                    },
                },
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                    },
                },
                zoom: false, // Disable zoom plugin entirely
            },
            interaction: {
                mode: 'index', // Disable zoom on interaction
                intersect: false,
            },
        },
    });

    // Expense Breakdown by Category Chart
    const ctx2 = document.getElementById('expenseBreakdownChart').getContext('2d');
    const expenseBreakdownChart = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: chartData.expenseBreakdownLabels,
            datasets: [{
                data: chartData.expenseBreakdownValues,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                ],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                    },
                },
                zoom: false, // Disable zoom plugin entirely
            },
            interaction: {
                mode: 'index', // Disable zoom on interaction
                intersect: false,
            },
        },
    });

    // Cash Flow Summary Chart
    const ctx3 = document.getElementById('cashFlowChart').getContext('2d');
    const cashFlowChart = new Chart(ctx3, {
        type: 'line',
        data: {
            labels: chartData.chartLabels,
            datasets: [{
                label: 'Net Savings',
                data: chartData.netSavingsTrend,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                        color: 'white',
                    },
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                        color: 'white',
                    },
                },
            },
            plugins: {
                legend: {
                    labels: {
                        color: 'white',
                    },
                },
                zoom: false, // Disable zoom plugin entirely
            },
            interaction: {
                mode: 'index', // Disable zoom on interaction
                intersect: false,
            },
        },
    });
});