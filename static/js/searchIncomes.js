// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');

// Get DOM elements
const searchField = document.querySelector('#searchField');
const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container');
const tableBody = document.querySelector('.table-body');

// Check if all required elements exist
if (!searchField || !tableOutput || !appTable || !paginationContainer || !tableBody) {
    console.error('Required DOM elements not found');
    return;
}

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
                tableBody.innerHTML = `
                    <tr style="border-bottom: 1px solid #4e4b4e;">
                        <td colspan="5" style="color: #f8f9fa; text-align: center; padding: 15px;">
                            <i class="fas fa-search" style="margin-right: 8px;"></i>No incomes match your search
                        </td>
                    </tr>`;
            } else {
                data.forEach((item) => {
                    const description = item.description.length > 30 ? 
                        item.description.substring(0, 30) + '...' : 
                        item.description;
                    
                    const date = new Date(item.date);
                    const formattedDate = date.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    });

                    tableBody.innerHTML += `
                        <tr style="border-bottom: 1px solid #4e4b4e;">
                            <td style="color: #4cc9f0; font-weight: 500;">${item.amount}</td>
                            <td>
                                <span class="badge" style="background-color: #3d5a5a; color: #f8f9fa;">
                                    ${item.source}
                                </span>
                            </td>
                            <td style="color: #f8f9fa;">${description}</td>
                            <td style="color: #a0a0a0;">${formattedDate}</td>
                            <td>
                                <a href="/edit-income/${item.id}/" class="btn btn-sm" style="background-color: #5a5a5a; color: #f8f9fa; margin-right: 5px;">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="/income-delete/${item.id}/" class="btn btn-danger btn-sm" onclick="return confirm('Are you sure you want to delete this income?')">
                                    <i class="fas fa-trash-alt"></i>
                                </a>
                            </td>
                        </tr>`;
                });
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            tableBody.innerHTML = `
                <tr style="border-bottom: 1px solid #4e4b4e;">
                    <td colspan="5" style="color: #f8f9fa; text-align: center; padding: 15px;">
                        <i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i>Error loading search results
                    </td>
                </tr>`;
        });
    } else {
        tableOutput.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
    }
});