document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('addTextbookBtn').addEventListener('click', function(event) {
        event.preventDefault();
        const isbn = document.getElementById('isbnInput').value.trim();
        if (isbn) {
            fetch('http://localhost:8000/textbooks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ isbn: isbn })  // Assuming you only need ISBN to add/update; add other fields as necessary
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('responseMessage').textContent = "Textbook added/updated successfully!";
                loadTextbooks(); // Reload the list of textbooks after adding/updating
            })
            .catch(error => {
                console.error('Error adding/updating textbook:', error);
                document.getElementById('responseMessage').textContent = 'Error adding/updating textbook: ' + error;
            });
        } else {
            document.getElementById('responseMessage').textContent = 'Please enter a valid ISBN.';
        }
    });
    document.getElementById('searchBtn').addEventListener('click', function(event) {
        event.preventDefault();
        const query = document.getElementById('searchInput').value.trim();
        if (query) {
            fetch(`http://localhost:8000/textbooks/search/?query=${query}`)
                
                .then(response => response.json())
                .then(data => {
                    const textbooksList = document.getElementById('textbooksList');
                    textbooksList.innerHTML = '';  // Clear existing content
                    if (data.books.length > 0) {
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
                            `;
                            textbooksList.appendChild(bookElement);
                        });                        
                    } else {
                        textbooksList.textContent = 'No textbooks found.';
                    }
                })
                .catch(error => {
                    console.error('Error searching textbooks:', error);
                    document.getElementById('responseMessage').textContent = 'Error searching textbooks: ' + error;
                });
        } else {
            document.getElementById('responseMessage').textContent = 'Please enter a search term.';
        }
    });
    

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
                                <p>Author(s): ${authors}</p>
                                <p>ISBN: ${book.isbn}</p>
                                <p>Published Date: ${book.published_date}</p>
                                <p>Description: ${book.description}</p>
                                <p>Subject: ${book.subject}</p>
                            </div>
                        </div>
                        <button onclick="deleteTextbook('${book.isbn}')">Delete</button>
                    `;
                    textbooksList.appendChild(bookElement);
                });
            })
            .catch(error => {
                console.error('Error loading textbooks:', error);
                document.getElementById('textbooksList').textContent = 'Failed to load textbooks.';
            });
    }
    
    window.deleteTextbook = function(isbn) {
        if (confirm('Are you sure you want to delete this textbook?')) {
            fetch(`http://localhost:8000/textbooks/${isbn}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('responseMessage').textContent = data.message;
                    loadTextbooks(); // Reload the list of textbooks after deleting
                })
                .catch(error => {
                    console.error('Error deleting textbook:', error);
                    document.getElementById('responseMessage').textContent = 'Error deleting textbook: ' + error;
                });
        }
    };

    loadTextbooks(); // Load textbooks on page load
});
