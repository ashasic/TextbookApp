document.addEventListener('DOMContentLoaded', function() {
    // Event listener for the "Add/Update Textbook" button
    document.getElementById('addTextbookBtn').addEventListener('click', function(event) {
        event.preventDefault();  // Prevent the default form submission if inside a form
        const isbn = document.getElementById('isbnInput').value.trim();
        if (isbn) {
            fetch('http://localhost:8000/textbooks/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ isbn: isbn })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    document.getElementById('responseMessage').textContent = data.message + ': ' + JSON.stringify(data.data);
                } else {
                    document.getElementById('responseMessage').textContent = 'Failed to add/update textbook.';
                }
                loadTextbooks(); // Reload the list of textbooks after adding/updating
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('responseMessage').textContent = 'Error adding/updating textbook: ' + error;
            });
        } else {
            document.getElementById('responseMessage').textContent = 'Please enter a valid ISBN.';
        }
    });

    // Function to load and display textbooks
    function loadTextbooks() {
        fetch('http://localhost:8000/textbooks/')
            .then(response => response.json())
            .then(data => {
                const textbooksList = document.getElementById('textbooksList');
                textbooksList.innerHTML = '';  // Clear existing content
                data.books.forEach(book => {
                    const bookElement = document.createElement('div');
                    bookElement.className = 'textbook';
                    bookElement.innerHTML = `
                        <h3>${book.title}</h3>
                        <img src="${book.thumbnail || 'path_to_default_image.jpg'}" alt="Cover image of ${book.title}" style="width:100px;"><br>
                        Author(s): ${book.authors.join(", ")}<br>
                        ISBN: ${book.isbn}<br>
                        Published Date: ${book.published_date}<br>
                        Description: ${book.description}<br>
                        Subject: ${book.subject}
                    `;
                    textbooksList.appendChild(bookElement);
                });
            })
            .catch(error => {
                console.error('Error loading textbooks:', error);
                document.getElementById('textbooksList').textContent = 'Failed to load textbooks.';
            });
    }

});
