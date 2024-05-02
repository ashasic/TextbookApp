document.addEventListener('DOMContentLoaded', function () {
    // Add Textbook Button
    const addTextbookBtn = document.getElementById('addTextbookBtn');
    if (addTextbookBtn) {
        addTextbookBtn.addEventListener('click', function (event) {
            event.preventDefault();
            const isbn = document.getElementById('isbnInput').value.trim();
            const responseMessage = document.getElementById('responseMessage');
            
            if (isbn) {
                fetch('http://localhost:8000/textbooks/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ isbn: isbn })
                })
                    .then(response => response.json())
                    .then(data => {
                        responseMessage.textContent = "Textbook added/updated successfully!";
                        loadTextbooks(); // Reload the list of textbooks after adding/updating
                    })
                    .catch(error => {
                        console.error('Error adding/updating textbook:', error);
                        responseMessage.textContent = 'Error adding/updating textbook: ' + error;
                    });
            } else {
                responseMessage.textContent = 'Please enter a valid ISBN.';
            }

            const homeBtn = document.getElementById('homeBtn');
            if (homeBtn) {
                homeBtn.style.display = 'none';
            }
        });
    }
    else {
        console.error('Button with ID "addTextbookBtn" not found');
    }
    

    // Search Button
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function (event) {
            event.preventDefault();
            const query = document.getElementById('searchInput').value.trim();
            const responseMessage = document.getElementById('responseMessage');

            if (query) {
                fetch(`http://localhost:8000/textbooks/search/?query=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        const textbooksList = document.getElementById('textbooksList');
                        textbooksList.innerHTML = '';  // Clear existing content
                        if (data.books.length > 0) {
                            const homeBtn = document.getElementById('homeBtn');
                            if (homeBtn) {
                                homeBtn.style.display = 'block';
                            }

                            data.books.forEach(book => {
                                const authors = Array.isArray(book.authors) ? book.authors.join(", ") : "No authors listed";
                                const bookElement = document.createElement('div');
                                bookElement.className = 'textbook';
                                bookElement.innerHTML = `
                                    <div class="textbook-info">
                                        <img src="${book.thumbnail || 'path_to_default_image.jpg'}" alt="Cover image of ${book.title}">
                                        <div class="textbook-details">
                                            <h3>${book.title}</h3>
                                            <p>Author(s): ${authors}</p>
                                            <p>ISBN: ${book.isbn}</p>
                                            <p>Published Date: ${book.published_date}</p>
                                            <p>Description: ${book.description}</p>
                                            <p>Subject: ${book.subject}</p>
                                        </div>
                                    </div>
                                    <button class="delete-btn" onclick="deleteTextbook('${book.isbn}')">Delete</button>
                                `;
                                textbooksList.appendChild(bookElement);
                            });
                        } else {
                            textbooksList.textContent = 'No textbooks found.';
                        }
                    })
                    .catch(error => {
                        console.error('Error searching textbooks:', error);
                        responseMessage.textContent = 'Error searching textbooks: ' + error;
                    });
            } else {
                responseMessage.textContent = 'Please enter a search term.';
            }
        });
    }

    // Home Button
    const homeBtn = document.getElementById('homeBtn');
    if (homeBtn) {
        homeBtn.addEventListener('click', function () {
            window.location.href = '/';
        });
    }

    // Load Textbooks
    function loadTextbooks() {
        fetch('http://localhost:8000/textbooks/')
            .then(response => response.json())
            .then(data => {
                console.log('Received textbooks:', data);  // Log the received data
                const textbooksList = document.getElementById('textbooksList');
                textbooksList.innerHTML = '';  // Clear existing content
                // Continue with forEach loop
                data.books.forEach(book => {
                    const authors = Array.isArray(book.authors) ? book.authors.join(", ") : "No authors listed";
                    const bookElement = document.createElement('div');
                    bookElement.className = 'textbook';
                    bookElement.innerHTML = `
                        <div class="textbook-info">
                            <img src="${book.thumbnail || 'path_to_default_image.jpg'}" alt="Cover image of ${book.title}">
                            <div class="textbook-details">
                                <h3>${book.title}</h3>
                                <p><b>Author(s):</b> ${authors}</p>
                                <p><b>ISBN:</b> ${book.isbn}</p>
                                <p><b>Published Date:</b> ${book.published_date}</p>
                                <p><b>Description:</b> ${book.description}</p>
                                <p><b>Subject:</b> ${book.subject}</p>
                            </div>
                        </div>
                        <button class="delete-btn" onclick="deleteTextbook('${book.isbn}')">Delete</button>
                    `;
                    textbooksList.appendChild(bookElement);
                });
            })
            .catch(error => {
                console.error('Error loading textbooks:', error);
                const textbooksList = document.getElementById('textbooksList');
                if (textbooksList) {
                    textbooksList.textContent = 'Failed to load textbooks.';
                }
            });
    }

    // Delete Textbook Function
    window.deleteTextbook = function (isbn) {
        if (confirm('Are you sure you want to delete this textbook?')) {
            fetch(`http://localhost:8000/textbooks/${isbn}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    const responseMessage = document.getElementById('responseMessage');
                    responseMessage.textContent = data.message;
                    loadTextbooks(); // Reload the list of textbooks after deleting
                })
                .catch(error => {
                    console.error('Error deleting textbook:', error);
                    const responseMessage = document.getElementById('responseMessage');
                    responseMessage.textContent = 'Error deleting textbook: ' + error;
                });
        }
    };

    // Load textbooks on page load
    const textbooksList = document.getElementById('textbooksList');
    if (textbooksList) {
        loadTextbooks();
    }
});