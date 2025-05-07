document.addEventListener('DOMContentLoaded', function () {
  // Container for showing validation/errors
  const responseMessage = document.getElementById('responseMessage');

  // Add Textbook Button
  const addTextbookBtn = document.getElementById('addTextbookBtn');
  if (addTextbookBtn) {
    addTextbookBtn.addEventListener('click', function (event) {
      event.preventDefault();
      const isbn = document.getElementById('isbnInput').value.trim();
      responseMessage.textContent = '';
      const token = localStorage.getItem('token'); // Get the JWT token

      if (isbn) {
        fetch('http://localhost:8000/textbooks/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ isbn: isbn })
        })
          .then(response => response.json())
          .then(data => {
            // handle expired‐signature
            if (data.detail === 'Signature has expired') {
              alert('Session expired. Please log in again.');
              localStorage.removeItem('token');
              return window.location.href = '/login';
            }

            if (data.detail) {
              responseMessage.textContent = Array.isArray(data.detail)
                ? data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('\n')
                : data.detail;
            } else {
              responseMessage.textContent = "Textbook added/updated successfully!";
              loadTextbooks(); // Reload the list of textbooks
            }
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
  } else {
    console.error('Button with ID "addTextbookBtn" not found');
  }

  // Search Button
  const searchBtn = document.getElementById('searchBtn');
  if (searchBtn) {
    searchBtn.addEventListener('click', function (event) {
      event.preventDefault();
      const query = document.getElementById('searchInput').value.trim();
      responseMessage.textContent = '';

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
                    … your existing HTML …
                    <button class="delete-btn" onclick="deleteTextbook('${book.isbn}')">Delete</button>
                    <button class="review-btn" onclick="goToReviewPage('${book.isbn}')">Review</button>
                `;
                // 1) Create a Details button:
                const detailsBtn = document.createElement('button');
                detailsBtn.textContent = 'New Listing +';
                detailsBtn.className = 'details-btn';
                detailsBtn.addEventListener('click', () => {
                  window.location.href = `/textbooks/${encodeURIComponent(book.isbn)}/detail`;
                });
                // 2) Append it:
                bookElement.appendChild(detailsBtn);

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
      .then(res => res.json())
      .then(data => {
        const textbooksList = document.getElementById('textbooksList');
        textbooksList.innerHTML = '';

        data.books.forEach(book => {
          const authors = Array.isArray(book.authors)
            ? book.authors.join(', ')
            : 'No authors listed';

          // build the card
          const bookElement = document.createElement('div');
          bookElement.className = 'textbook';
          bookElement.innerHTML = `
            <div class="textbook-info">
              <img
                src="${book.thumbnail || '/static/images/default_book_cover.jpg'}"
                alt="Cover of ${book.title}"
              >
              <div class="textbook-details">
                <h3>${book.title}</h3>
                <p><b>Authors:</b> ${authors}</p>
                <p><b>ISBN:</b> ${book.isbn}</p>
                <p><b>Published:</b> ${book.published_date}</p>
              </div>
            </div>
            <div class="actions">
              <button class="details-btn">TRADE</button>
            </div>
          `;

          // 1) entire card click → view page
          bookElement.addEventListener('click', () => {
            window.location.href = `/textbooks/${encodeURIComponent(book.isbn)}/view`;
          });

          // 2) prevent the inner button from triggering the card click
          const detailsBtn = bookElement.querySelector('.details-btn');
          detailsBtn.addEventListener('click', e => {
            e.stopPropagation();
            window.location.href = `/textbooks/${encodeURIComponent(book.isbn)}/view`;
          });

          textbooksList.appendChild(bookElement);
        });
      })
      .catch(err => {
        console.error('Error loading textbooks:', err);
        responseMessage.textContent = 'Failed to load textbooks.';
      });
  }

  // Function to redirect to the review page
  window.goToReviewPage = function (isbn) {
    window.location.href = `/reviews.html?isbn=${isbn}`;
  }

  // Delete Textbook Function
  window.deleteTextbook = function (isbn) {
    if (confirm('Are you sure you want to delete this textbook?')) {
      fetch(`http://localhost:8000/textbooks/${isbn}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
          responseMessage.textContent = data.message;
          loadTextbooks(); // Reload the list of textbooks after deleting
        })
        .catch(error => {
          console.error('Error deleting textbook:', error);
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
