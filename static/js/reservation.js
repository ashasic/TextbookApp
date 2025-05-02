document.addEventListener('DOMContentLoaded', function() {
    const fetchDetailsBtn = document.getElementById('fetchDetailsBtn');
    const isbnOrTitleInput = document.getElementById('isbnOrTitleInput');
    const textbooksList = document.getElementById('textbooksList');

    function displayTextbookDetails(book) {
        const authors = Array.isArray(book.authors) ? book.authors.join(", ") : "No authors listed";
        const bookElement = document.createElement('div');
        bookElement.className = 'textbook';
        bookElement.innerHTML = `
            <div class="textbook-info">
                <img src="${book.thumbnail || '/static/images/default_book_cover.jpg'}" alt="Cover image of ${book.title}">
                <div class="textbook-details">
                    <h3>${book.title}</h3>
                    <p>Author(s): ${authors}</p>
                    <p>ISBN: ${book.isbn}</p>
                    <p>Published Date: ${book.published_date}</p>
                    <p>Description: ${book.description}</p>
                    <p>Subject: ${book.subject}</p>
                </div>
            </div>`;
        const reserveButton = document.createElement('button');
        reserveButton.textContent = 'Reserve';
        reserveButton.className = 'reserve-btn';
        reserveButton.addEventListener('click', function() {
            makeReservation(book);
            isbnOrTitleInput.value = '';
        });
        bookElement.appendChild(reserveButton);
        textbooksList.appendChild(bookElement);
        textbooksList.style.display = 'block';
    }

    fetchDetailsBtn.addEventListener('click', function(event) {
        event.preventDefault();
        const query = isbnOrTitleInput.value.trim();
        if (!query) {
            alert('Please enter an ISBN or Title.');
            return;
        }
        fetch(`http://localhost:8000/textbooks/search/?query=${query}`)
            .then(response => response.json())
            .then(data => {
                if (data.books.length > 0) {
                    textbooksList.innerHTML = '';
                    data.books.forEach(displayTextbookDetails);
                } else {
                    alert('No textbook found with the provided details.');
                    textbooksList.innerHTML = '';
                    textbooksList.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching textbook details:', error);
                alert('Error fetching textbook details: ' + error);
            });
    });

    function makeReservation(book) {
        const bookDetails = {
            isbn: book.isbn,
            title: book.title,
            authors: book.authors.join(", "),
            published_date: book.published_date,
            description: book.description,
            subject: book.subject,
            user: 'your-username' // This should be dynamically set based on user session or similar
        };

        fetch('http://localhost:8000/reservations/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookDetails)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Failed to create reservation');
                });
            }
        })
        .then(data => {
            alert('Reservation successful!');
            console.log('Reservation created:', data);
        })
        .catch(error => {
            console.error('Error creating reservation:', error);
            alert('Error creating reservation: ' + error.message);
        });
    }
});
