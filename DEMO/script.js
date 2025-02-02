const API_BASE = "http://localhost:8000";

// Fetch users
function getUsers() {
    fetch(`${API_BASE}/users/get_all_users`)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("usersList");
            list.innerHTML = "";
            data.forEach(user => {
                list.innerHTML += `<li>${user.name} (${user.email}) 
                    <button onclick="deleteUser('${user.email}')">Delete</button>
                </li>`;
            });
        });
}

// Add user
function addUser() {
    const name = document.getElementById("userName").value;
    const email = document.getElementById("userEmail").value;

    fetch(`${API_BASE}/users/add_user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: Math.random(), name, email })
    }).then(() => getUsers());
}

// Delete user
function deleteUser(email) {
    fetch(`${API_BASE}/users/delete_user?email=${email}`, { method: "DELETE" })
        .then(() => getUsers());
}

// Fetch categories
function getCategories() {
    fetch(`${API_BASE}/categories/get_all_categories`)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("categoriesList");
            list.innerHTML = "";
            data.forEach(category => {
                list.innerHTML += `<li>${category.name} 
                    <button onclick="deleteCategory(${category.id})">Delete</button>
                </li>`;
            });
        });
}

// Add category
function addCategory() {
    const name = document.getElementById("categoryName").value;

    fetch(`${API_BASE}/categories/add_category`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    }).then(() => getCategories());
}

// Delete category
function deleteCategory(id) {
    fetch(`${API_BASE}/categories/delete_category?id=${id}`, { method: "DELETE" })
        .then(() => getCategories());
}

// Fetch transactions
function getTransactions() {
    fetch(`${API_BASE}/transactions/get_all_transactions`)
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("transactionsList");
            list.innerHTML = "";
            data.forEach(transaction => {
                list.innerHTML += `<li>${transaction.date} - $${transaction.amount} 
                    <button onclick="deleteTransaction(${transaction.id})">Delete</button>
                </li>`;
            });
        });
}

// Add transaction
function addTransaction() {
    const userId = document.getElementById("transactionUserId").value;
    const date = document.getElementById("transactionDate").value;
    const amount = document.getElementById("transactionAmount").value;
    const categoryId = document.getElementById("transactionCategoryId").value;
    const source = document.getElementById("transactionSource").value;
    const recurring = document.getElementById("transactionRecurring").value;

    fetch(`${API_BASE}/transactions/add_transaction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id: Math.random(),
            user_id: parseInt(userId),
            date,
            amount: parseFloat(amount),
            category_id: parseInt(categoryId),
            source,
            recurring
        })
    }).then(() => getTransactions());
}

// Delete transaction
function deleteTransaction(id) {
    fetch(`${API_BASE}/transactions/delete_transaction?id=${id}`, { method: "DELETE" })
        .then(() => getTransactions());
}

// Load data on page load
window.onload = () => {
    getUsers();
    getCategories();
    getTransactions();
};
