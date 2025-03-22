document.addEventListener("DOMContentLoaded", function () {
    fetch("/expense_category_summary")
        .then((response) => response.json())
        .then((result) => {
            console.log("Expense Summary Data:", result);

            // Check if data is valid
            if (!result || !result.expense_category_data || Object.keys(result.expense_category_data).length === 0) {
                console.error("No valid data received");
                document.getElementById("totalAmount").textContent = "No expenses data available";
                return;
            }

            const data = result.expense_category_data;
            const categories = Object.keys(data);
            const amounts = Object.values(data);
            const currency = result.currency || "USD";
            const totalAmount = Number(result.total_amount) || 0; // Ensure number type

            // Safely get values with fallbacks and type conversion
            const averageExpenses = Number(result.average_expenses) || 0;
            const maxCategory = result.max_category ? String(result.max_category) : "N/A";
            const minCategory = result.min_category ? String(result.min_category) : "N/A";
            const essentialAmount = Number(result.essential_amount) || 0;
            const nonEssentialAmount = Number(result.non_essential_amount) || 0;
            const expenseTrend = Number(result.expense_trend) || 0; // Ensure expenseTrend is defined and a number

            // Calculate percentages safely
            const percentageCalc = (value) => {
                return totalAmount > 0 ? ((value / totalAmount) * 100).toFixed(2) : "0.00";
            };

            // Update total amount display
            document.getElementById("totalAmount").textContent = 
                `${currency} ${totalAmount.toFixed(2)}`;

            // Update insights with safe value handling
            const insightsContainer = document.getElementById("insightsContainer");
            insightsContainer.innerHTML = `
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Average Expenses</h6>
                        <p class="text-white fs-5">${currency} ${averageExpenses.toFixed(2)}</p>
                        <small class="text-white-50">${percentageCalc(averageExpenses)}% of total</small>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Maximum Expense Category</h6>
                        <p class="text-white fs-5">${maxCategory}</p>
                        ${maxCategory !== "N/A" && data.hasOwnProperty(maxCategory) ? `
                            <p class="text-white fs-5">${currency} ${data[maxCategory].toFixed(2)}</p>
                            <small class="text-white-50">${percentageCalc(data[maxCategory])}% of total</small>
                        ` : ''}
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Minimum Expense Category</h6>
                        <p class="text-white fs-5">${minCategory}</p>
                        ${minCategory !== "N/A" && data.hasOwnProperty(minCategory) ? `
                            <p class="text-white fs-5">${currency} ${data[minCategory].toFixed(2)}</p>
                            <small class="text-white-50">${percentageCalc(data[minCategory])}% of total</small>
                        ` : ''}
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Essential Expenses</h6>
                        <p class="text-white fs-5">${currency} ${essentialAmount.toFixed(2)}</p>
                        <small class="text-white-50">${percentageCalc(essentialAmount)}% of total</small>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Non-Essential Expenses</h6>
                        <p class="text-white fs-5">${currency} ${nonEssentialAmount.toFixed(2)}</p>
                        <small class="text-white-50">${percentageCalc(nonEssentialAmount)}% of total</small>
                    </div>
                </div>
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 shadow-sm p-3">
                        <h6 class="text-white mb-2">Expense Trend</h6>
                        <p class="text-white fs-5">${expenseTrend.toFixed(2)}%</p>
                    </div>
                </div>
            `;

            // Initialize charts
            if (categories.length > 0 && amounts.length > 0) {
                // Bar Chart
                new Chart(document.getElementById("barChart").getContext("2d"), {
                    type: "bar",
                    data: {
                        labels: categories,
                        datasets: [{
                            label: `Amount (${currency})`,
                            data: amounts,
                            backgroundColor: "rgba(221, 41, 32, 0.8)",
                            borderColor: "rgb(49, 144, 63)",
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        const label = context.label || "";
                                        const value = context.raw || 0;
                                        const percentage = ((value / totalAmount) * 100).toFixed(2);
                                        return `${label}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                    },
                                },
                            },
                        },
                    }
                });

                // Pie Chart
                new Chart(document.getElementById("pieChart").getContext("2d"), {
                    type: "pie",
                    data: {
                        labels: categories,
                        datasets: [{
                            data: amounts,
                            backgroundColor: [
                                "#FF6384", "#36A2EB", "#FFCE56", 
                                "#4BC0C0", "#9966FF", "#FF9F40"
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        const label = context.label || "";
                                        const value = context.raw || 0;
                                        const percentage = ((value / totalAmount) * 100).toFixed(2);
                                        return `${label}: ${currency} ${value.toFixed(2)} (${percentage}%)`;
                                    },
                                },
                            },
                        },
                    }
                });
            }
        })
        .catch((error) => {
            console.error("Fetch error:", error);
            document.getElementById("totalAmount").textContent = "Error loading data";
        });
});