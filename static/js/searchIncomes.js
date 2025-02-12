const searchField = document.querySelector('#searchField');
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container');
const tableBody = document.querySelector('.table-body');

tableOutput.style.display = 'none';

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        paginationContainer.style.display = "none";
        tableBody.innerHTML = "";

        fetch("/search-incomes/", {
            method: "POST",
            body: JSON.stringify({ searchText: searchValue }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            appTable.style.display = "none";
            tableOutput.style.display = "block";

            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5">No results found</td></tr>';
            } else {
                data.forEach((item) => {
                    tableBody.innerHTML += `
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.source}</td>
                            <td>${item.description}</td>
                            <td>${item.date}</td>
                            <td>
                                <a href="/edit-income/${item.id}/" class="btn btn-secondary btn-sm">Edit</a>
                                <a href="/income-delete/${item.id}/" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to delete this income?')">Delete</a>
                            </td>
                        </tr>`;
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});