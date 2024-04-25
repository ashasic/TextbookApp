// When the document content is fully loaded, execute the getExpenses function
document.addEventListener('DOMContentLoaded', () => {
    getExpenses();
});

const api = 'http://127.0.0.1:8000/expenses'; // Base API URL for expense operations

// DOM element references for form and table
const form = document.getElementById('expenseForm');
const expensesTable = document.getElementById('expensesTable').getElementsByTagName('tbody')[0];
let data = []; // Array to hold expense data for client-side processing

// Event listener for form submission to add a new expense
form.addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Constructing expense object from form data
    const expense = {
        date: form.date.value, // ISO format is okay for backend
        category: form.category.value,
        amount: parseFloat(form.amount.value),
        description: form.description.value || '' // Description is optional
    };
    
    addExpense(expense); // Call function to add expense
});

// Function to add an expense via POST request
function addExpense(expense) {
    fetch(api, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(expense),
    })
    .then(response => response.json())
    .then(newExpense => {
        console.log('Success:', newExpense);
        form.reset(); // Reset form fields after successful submission
        getExpenses(); // Reload the list of expenses to include the new one
    })
    
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to fetch and display all expenses
function getExpenses() {
    fetch(api)
    .then(response => response.json())
    .then(fetchedData => {
        data = fetchedData; // Update the global data array
        refreshExpenses(data); // Pass the data to the refresh function
    })

    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to update the expenses table in the UI
function refreshExpenses(data) {

    expensesTable.innerHTML = ''; // Clear existing table rows

    data.forEach(expense => {
        const row = expensesTable.insertRow(); // Insert a new row in the table
        row.setAttribute('id', `expense-${expense.id}`); // Set an ID for the row for later reference
        row.innerHTML = `
            <td>${formatDateFromISO(expense.date)}</td>
            <td>${expense.category}</td>
            <td>$${parseFloat(expense.amount).toFixed(2)}</td>
            <td>${expense.description}</td>
            <td>
                <button class="edit-button" onclick="editExpense(${expense.id})">Edit</button>
                <button class="delete-button" onclick="deleteExpense(${expense.id})">Delete</button>
            </td>
        `;
    });
}

// Function to delete an expense via DELETE request
function deleteExpense(id) {
    fetch(`${api}/${id}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (response.ok) {
            getExpenses(); // Refresh the list after deletion
        }
    })

    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to enable editing of an expense
function editExpense(id) {
    const expense = data.find(x => x.id === id); // Find the expense in the data array
    const expenseRow = document.querySelector(`#expense-${id}`); // Get the corresponding table row
    const cells = expenseRow.querySelectorAll('td'); // Get all cells (td elements) of the row

    // Replace table cells content with input fields, pre-filled with existing expense data
    cells[0].innerHTML = `<input type="date" value="${expense.date.split('T')[0]}" id="edit-date-${id}">`;
    cells[1].innerHTML = `
        <select id="edit-category-${id}">
            <option value="Food">Food</option>
            <option value="Transportation">Transportation</option>
            <option value="Housing">Housing</option>
            <option value="Utilities">Utilities</option>
            <option value="Entertainment">Entertainment</option>
            <option value="Other">Other</option>
        </select>`;
    cells[2].innerHTML = `<input type="number" value="${expense.amount}" id="edit-amount-${id}" step="0.01">`;
    cells[3].innerHTML = `<input type="text" value="${expense.description}" id="edit-description-${id}">`;
    // Add Save and Cancel buttons for editing
    cells[4].innerHTML = `
        <button class="save-button" onclick="saveExpense(${id})">Save</button>
        <button class="cancel-button" onclick="getExpenses()">Cancel</button>
    `;

    document.querySelector(`#edit-category-${id}`).value = expense.category; // Set the current category as selected
}

// Function to save the updated expense via PUT request
function saveExpense(id) {
    const updatedExpense = {
        date: document.getElementById(`edit-date-${id}`).value,
        category: document.getElementById(`edit-category-${id}`).value,
        amount: parseFloat(document.getElementById(`edit-amount-${id}`).value),
        description: document.getElementById(`edit-description-${id}`).value,
    };

    fetch(`${api}/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedExpense),
    })
    .then(response => {
        if (response.ok) {
            getExpenses(); // Refresh the list after saving
        }
    })

    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to convert date from ISO format to MM/DD/YYYY for display
function formatDateFromISO(isoString) {
    if (!isoString) return '';
    const [year, month, day] = isoString.split('-');
    return `${month}/${day}/${year}`;
}
