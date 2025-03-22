document.addEventListener("DOMContentLoaded", function () {
    fetch("/incomes/income-category-summary/")
        .then((response) => response.json())
        .then((result) => {
            console.log("Income Summary Data:", result);

            if (!result || !result.income_source_data || !result.currency) {
                console.error("Invalid or incomplete data received from the server.");
                return;
            }

            const incomeSourceData = result.income_source_data || {};
            const incomePercentages = result.income_percentages || {};
            const monthlyIncomeData = result.monthly_income_data || {};
            const dailyIncomeData = result.daily_income_data || {};
            const currency = result.currency || "USD";

            const totalIncome = Object.values(incomeSourceData).reduce((sum, amount) => sum + amount, 0);
            document.getElementById("totalIncome").textContent = `${currency} ${totalIncome.toFixed(2)}`;

            const insightsContainer = document.getElementById("insightsContainer");
            insightsContainer.innerHTML = `
                <div class="col-md-6 mb-4">
                    <div class="card bg-gradient-primary border-0 shadow-lg p-3 hover-scale">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-chart-line fa-2x text-white me-3"></i>
                            <div>
                                <h6 class="text-white mb-2">Top 3 Income Sources</h6>
                                <p class="text-white fs-5">
                                    ${result.top_3_sources?.names[0] || "N/A"} (${currency} ${(result.top_3_sources?.amounts[0] || 0).toFixed(2)}), 
                                    ${result.top_3_sources?.names[1] || "N/A"} (${currency} ${(result.top_3_sources?.amounts[1] || 0).toFixed(2)}), 
                                    ${result.top_3_sources?.names[2] || "N/A"} (${currency} ${(result.top_3_sources?.amounts[2] || 0).toFixed(2)})
                                </p>
                                <small class="text-white-50">${(result.top_3_sources?.percentages[0] || 0).toFixed(2)}%, ${(result.top_3_sources?.percentages[1] || 0).toFixed(2)}%, ${(result.top_3_sources?.percentages[2] || 0).toFixed(2)}% of total income</small>
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
                                <p class="text-white fs-5">${currency} ${(result.average_income?.amount || 0).toFixed(2)}</p>
                                <small class="text-white-50">${(result.average_income?.percentage || 0).toFixed(2)}% of total income</small>
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
                                <p class="text-white fs-5">${result.max_peaked_month?.name || "N/A"} (${currency} ${(result.max_peaked_month?.amount || 0).toFixed(2)})</p>
                                <small class="text-white-50">${(result.max_peaked_month?.percentage || 0).toFixed(2)}% of total income</small>
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
                                <p class="text-white fs-5">${result.min_income_source?.name || "N/A"} (${currency} ${(result.min_income_source?.amount || 0).toFixed(2)})</p>
                                <small class="text-white-50">${(result.min_income_source?.percentage || 0).toFixed(2)}% of total income</small>
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
                                <p class="text-white fs-5">${(result.growth_rate || 0).toFixed(2)}%</p>
                                <small class="text-white-50">Compared to previous period</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            if (Object.keys(incomeSourceData).length > 0) {
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
                                        const percentage = incomePercentages[label] || 0;
                                        return `${label}: ${currency} ${value.toFixed(2)} (${percentage.toFixed(2)}%)`;
                                    },
                                },
                            },
                        },
                    },
                });
            } else {
                console.error("No data available to render the pie chart.");
            }

            if (Object.keys(monthlyIncomeData).length > 0) {
                const barChartCtx = document.getElementById("barChart").getContext("2d");
                new Chart(barChartCtx, {
                    type: "bar",
                    data: {
                        labels: Object.keys(monthlyIncomeData),
                        datasets: [{
                            label: `Amount (${currency})`,
                            data: Object.values(monthlyIncomeData),
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
                                        const label = context.label || "";
                                        const value = context.raw || 0;
                                        const percentage = ((value / totalIncome) * 100).toFixed(2);
                                        return `${label}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                    },
                                },
                            },
                        },
                    },
                });
            } else {
                console.error("No data available to render the bar chart.");
            }

            if (Object.keys(dailyIncomeData).length > 0) {
                const lineChartCtx = document.getElementById("lineChart").getContext("2d");
                new Chart(lineChartCtx, {
                    type: "line",
                    data: {
                        labels: Object.keys(dailyIncomeData),
                        datasets: [{
                            label: `Amount (${currency})`,
                            data: Object.values(dailyIncomeData),
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
                                        const label = context.label || "";
                                        const value = context.raw || 0;
                                        const percentage = ((value / totalIncome) * 100).toFixed(2);
                                        const source = result.daily_income_source?.[label] || "Unknown Source";
                                        return `${label}: ${currency} ${value.toFixed(2)} (${percentage}%) - Source: ${source}`;
                                    },
                                },
                            },
                        },
                    },
                });
            } else {
                console.error("No data available to render the line chart.");
            }
        })
        .catch((error) => {
            console.error("Error fetching income summary data:", error);
        });
});