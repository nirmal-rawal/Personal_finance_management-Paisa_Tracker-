const searchField = document.querySelector('#searchField');
const tableOutput= document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container');
const tableBody = document.querySelector('.table-body')
tableOutput.style.display='none';
searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;

    if (searchValue.trim().length > 0) {
        paginationContainer.style.display="none";
        tableBody.innerHTML="";
        console.log("searchValue", searchValue);

        fetch("/search-expenses/", {
            method: "POST",
            body: JSON.stringify({ searchText: searchValue }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // ✅ Fixed: CSRF Token is now defined
            },
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            appTable.style.display="none";

            tableOutput.style.display="block";

            if (data.length===0){
                tableOutput.innerHTML='No result found';

            }else{
                data.forEach(item=>{
                    tableBody.innerHTML+=`
                <tr>
                <td>${item.amount}</td>
                <td>${item.category}</td>
                <td>${item.description}</td>
                <td>${item.date}</td>
                </tr>`;
                    
                });

                

                    
            }

        })
        
        
        .catch(error => console.error("Error:", error));
        
    }else{
        tableOutput.style.display="none";
        appTable.style.display="block";
        paginationContainer.style.display="block";
    }
});