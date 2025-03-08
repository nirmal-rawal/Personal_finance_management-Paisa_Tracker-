document.addEventListener("DOMContentLoaded", function () {
    fetch("/incomes/income-category-summary/")
        .then((response) => response.json())
        .then((result) => {
            const incomeSourceData = result.income_source_data;
            const incomePercentages = result.income_percentages;
            const monthlyIncomeData = result.monthly_income_data;
            const dailyIncomeData = result.daily_income_data;
            const currency = result.currency;

            // Calculate total income
            const totalIncome = Object.values(incomeSourceData).reduce((sum, amount) => sum + amount, 0);
            document.getElementById("totalIncome").textContent = `${currency} ${totalIncome.toFixed(2)}`;

            // Display insights dynamically
            const insightsContainer = document.getElementById("insightsContainer");
            insightsContainer.innerHTML = `
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-primary border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-chart-line fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Top 3 Income Sources</h6>
                                <p class="text-white fs-5">
                                    ${result.top_3_sources.names[0]} (${currency} ${result.top_3_sources.amounts[0].toFixed(2)}), 
                                    ${result.top_3_sources.names[1]} (${currency} ${result.top_3_sources.amounts[1].toFixed(2)}), 
                                    ${result.top_3_sources.names[2]} (${currency} ${result.top_3_sources.amounts[2].toFixed(2)})
                                </p>
                                <small class="text-white-50">${result.top_3_sources.percentages[0].toFixed(2)}%, ${result.top_3_sources.percentages[1].toFixed(2)}%, ${result.top_3_sources.percentages[2].toFixed(2)}% of total income</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-danger border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-dollar-sign fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Average Income</h6>
                                <p class="text-white fs-5">${currency} ${result.average_income.amount.toFixed(2)}</p>
                                <small class="text-white-50">${result.average_income.percentage.toFixed(2)}% of total income</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-warning border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-arrow-up fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Maximum Peaked Month</h6>
                                <p class="text-white fs-5">${result.max_peaked_month.name} (${currency} ${result.max_peaked_month.amount.toFixed(2)})</p>
                                <small class="text-white-50">${result.max_peaked_month.percentage.toFixed(2)}% of total income</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-success border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-arrow-down fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Minimum Income Source</h6>
                                <p class="text-white fs-5">${result.min_income_source.name} (${currency} ${result.min_income_source.amount.toFixed(2)})</p>
                                <small class="text-white-50">${result.min_income_source.percentage.toFixed(2)}% of total income</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-info border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-chart-bar fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Growth Rate (Last 3 Months)</h6>
                                <p class="text-white fs-5">${result.growth_rate.toFixed(2)}%</p>
                                <small class="text-white-50">Compared to previous period</small>
                            </div>
                        </div>
                    </div>
                </div>
                
            `;

            // Pie Chart (Income Distribution by Category)
            const pieChartCtx = document.getElementById("pieChart").getContext("2d");
            new Chart(pieChartCtx, {
                type: "pie",
                data: {
                    labels: Object.keys(incomeSourceData),
                    datasets: [{
                        label: `Amount (${currency})`,
                        data: Object.values(incomeSourceData),
                        backgroundColor: [
                            "rgba(255, 99, 132, 0.8)",
                            "rgba(54, 162, 235, 0.8)",
                            "rgba(255, 206, 86, 0.8)",
                            "rgba(75, 192, 192, 0.8)",
                            "rgba(153, 102, 255, 0.8)",
                            "rgba(255, 159, 64, 0.8)",
                        ],
                        borderColor: [
                            "rgba(255, 99, 132, 1)",
                            "rgba(54, 162, 235, 1)",
                            "rgba(255, 206, 86, 1)",
                            "rgba(75, 192, 192, 1)",
                            "rgba(153, 102, 255, 1)",
                            "rgba(255, 159, 64, 1)",
                        ],
                        borderWidth: 1,
                    }],
                },
                options: {
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.label || "";
                                    const value = context.raw || 0;
                                    const percentage = incomePercentages[label].toFixed(2);
                                    return `${label}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                },
                            },
                        },
                        datalabels: {
                            formatter: (value, context) => {
                                const label = context.chart.data.labels[context.dataIndex];
                                const percentage = incomePercentages[label].toFixed(2);
                                return `${percentage}%`;
                            },
                            color: "#ffffff", // White text color
                            font: {
                                weight: "bold",
                                size: 14,
                            },
                            textShadowColor: "rgba(0, 0, 0, 0.8)", // Add shadow for better visibility
                            textShadowBlur: 5,
                        },
                        legend: {
                            labels: {
                                color: "white",
                            },
                        },
                    },
                },
                plugins: [ChartDataLabels], // Enable the datalabels plugin
            });

            // Bar Chart (Monthly Income Trends)
            const barChartCtx = document.getElementById("barChart").getContext("2d");
            new Chart(barChartCtx, {
                type: "bar",
                data: {
                    labels: Object.keys(monthlyIncomeData),
                    datasets: [{
                        label: `Amount (${currency})`,
                        data: Object.values(monthlyIncomeData).map((amount, index) => ({
                            x: Object.keys(monthlyIncomeData)[index], // Month
                            y: amount, // Amount
                            source: Object.keys(incomeSourceData)[index % Object.keys(incomeSourceData).length], // Source of income
                            percentage: ((amount / totalIncome) * 100).toFixed(2), // Percentage of total income
                        })),
                        backgroundColor: "rgba(75, 192, 192, 0.8)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    }],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Amount",
                                color: "white",
                            },
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                        x: {
                            title: {
                                display: true,
                                text: "Month",
                                color: "white",
                            },
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.raw.x; // Month
                                    const value = context.raw.y; // Amount
                                    const source = context.raw.source; // Source of income
                                    const percentage = context.raw.percentage; // Percentage of total income
                                    return `${source}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                },
                            },
                        },
                        legend: {
                            labels: {
                                color: "white",
                            },
                        },
                    },
                },
            });

            // Line Chart (Daily Income Growth)
            const lineChartCtx = document.getElementById("lineChart").getContext("2d");
            new Chart(lineChartCtx, {
                type: "line",
                data: {
                    labels: Object.keys(dailyIncomeData),
                    datasets: [{
                        label: `Amount (${currency})`,
                        data: Object.values(dailyIncomeData).map((amount, index) => ({
                            x: Object.keys(dailyIncomeData)[index], // Day
                            y: amount, // Amount
                            source: Object.keys(incomeSourceData)[index % Object.keys(incomeSourceData).length], // Source of income
                            percentage: ((amount / totalIncome) * 100).toFixed(2), // Percentage of total income
                        })),
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 2,
                        fill: false,
                    }],
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Income",
                                color: "white",
                            },
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                        x: {
                            title: {
                                display: true,
                                text: "Date",
                                color: "white",
                            },
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const label = context.raw.x; // Day
                                    const value = context.raw.y; // Amount
                                    const source = context.raw.source; // Source of income
                                    const percentage = context.raw.percentage; // Percentage of total income
                                    return `${source}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                },
                            },
                        },
                        legend: {
                            labels: {
                                color: "white",
                            },
                        },
                    },
                },
            });
        })
        .catch((error) => {
            console.error("Error fetching income summary data:", error);
        });
});