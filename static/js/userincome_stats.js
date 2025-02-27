document.addEventListener("DOMContentLoaded", function () {
    fetch("/incomes/income-category-summary/")  // Include the app's base path
        .then((response) => response.json())
        .then((result) => {
            const incomeSourceData = result.income_source_data;
            const monthlyIncomeData = result.monthly_income_data;
            const dailyIncomeData = result.daily_income_data;
            const currency = result.currency;

            // Calculate total income
            const totalIncome = Object.values(incomeSourceData).reduce((sum, amount) => sum + amount, 0);
            document.getElementById("totalIncome").textContent = `${currency} ${totalIncome.toFixed(2)}`;

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
                        legend: {
                            labels: {
                                color: "white",
                            },
                        },
                    },
                },
            });

            // Bar Chart (Monthly Income Trends)
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
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                        x: {
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                    },
                    plugins: {
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
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                        x: {
                            grid: {
                                color: "rgba(255, 255, 255, 0.1)",
                            },
                            ticks: {
                                color: "white",
                            },
                        },
                    },
                    plugins: {
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