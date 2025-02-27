document.addEventListener("DOMContentLoaded", function () {
    fetch("/expense_category_summary")
        .then((response) => response.json())
        .then((result) => {
            const data = result.expense_category_data;
            const categories = Object.keys(data);
            const amounts = Object.values(data);
            const percentages = Object.values(result.percentages);
            const currency = result.currency;
            const totalAmount = result.total_amount;
            const datesByCategory = result.dates_by_category;
            const averageExpenses = result.average_expenses;
            const maxCategory = result.max_category;
            const minCategory = result.min_category;
            const expenseTrend = result.expense_trend;
            const essentialAmount = result.essential_amount;
            const nonEssentialAmount = result.non_essential_amount;

            // Display total amount with user's preferred currency
            document.getElementById("totalAmount").textContent = `${currency} ${totalAmount.toFixed(2)}`;

           // Display additional insights
const insightsContainer = document.getElementById("insightsContainer");
insightsContainer.innerHTML = `
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Average Expenses</h6>
            <p class="text-white fs-5">${currency} ${averageExpenses.toFixed(2)}</p>
            <small class="text-white-50">${((averageExpenses / totalAmount) * 100).toFixed(2)}% of total amount amountc</small>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Maximum Expense Category</h6>
            <p class="text-white fs-5">${maxCategory} (${currency} ${data[maxCategory].toFixed(2)})</p>
            <small class="text-white-50">${((data[maxCategory] / totalAmount) * 100).toFixed(2)}% of total amount</small>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Minimum Expense Category</h6>
            <p class="text-white fs-5">${minCategory} (${currency} ${data[minCategory].toFixed(2)})</p>
            <small class="text-white-50">${((data[minCategory] / totalAmount) * 100).toFixed(2)}% of total amount</small>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Expense Trend</h6>
            <p class="text-white fs-5">${expenseTrend.toFixed(2)}%</p>
            <small class="text-white-50">Compared to previous period</small>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Essential Expenses</h6>
            <p class="text-white fs-5">${currency} ${essentialAmount.toFixed(2)}</p>
            <small class="text-white-50">${((essentialAmount / totalAmount) * 100).toFixed(2)}% of total</small>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card bg-secondary border-0 shadow-sm p-3">
            <h6 class="text-white mb-2">Non-Essential Expenses</h6>
            <p class="text-white fs-5">${currency} ${nonEssentialAmount.toFixed(2)}</p>
            <small class="text-white-50">${((nonEssentialAmount / totalAmount) * 100).toFixed(2)}% of total amount</small>
        </div>
    </div>
`;
            // Bar Chart
            const barChartCtx = document.getElementById("barChart").getContext("2d");
            new Chart(barChartCtx, {
                type: "bar",
                data: {
                    labels: categories,
                    datasets: [{
                        label: `Amount (${currency})`,
                        data: amounts,
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

            // Pie Chart
            const pieChartCtx = document.getElementById("pieChart").getContext("2d");
            new Chart(pieChartCtx, {
                type: "pie",
                data: {
                    labels: categories,
                    datasets: [{
                        label: "Amount",
                        data: amounts,
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
                        datalabels: {
                            color: "white",
                            font: {
                                weight: "bold",
                                size: 14,
                            },
                            formatter: function (value, context) {
                                return `${percentages[context.dataIndex].toFixed(2)}%`;
                            },
                        },
                    },
                },
                plugins: [ChartDataLabels],
            });
        });
});