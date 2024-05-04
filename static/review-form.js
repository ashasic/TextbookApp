document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('reviewForm');
    const isbnInput = document.getElementById('isbn');
    const reviewInput = document.getElementById('review');
    const params = new URLSearchParams(window.location.search);
    const isbn = params.get('isbn');
    console.log('ISBN:', isbn);
    const token = localStorage.getItem('token'); // JWT token from local storage

    if (!isbn) {
        alert('ISBN not specified');
        return;
    }

    // Set the ISBN hidden field value
    isbnInput.value = isbn;

    // Fetch user data from the backend using /login/ endpoint
    fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            // Add any necessary credentials here
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch current user data');
        }
        return response.json();
    })
    .then(userData => {
        const user = userData.user; // Assuming the user data contains the user object
        console.log('Current User:', user);

        // Load review for editing, if ID is specified
        if (user) {
            fetch(`http://localhost:8000/reviews/${isbn}/${user.username}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load review');
                }
                return response.json();
            })
            .then(data => {
                reviewInput.value = data.review;
            })
            .catch(error => {
                console.error('Error loading review:', error);
                alert('Failed to load review');
            });
        }
    })
    .catch(error => {
        console.error('Error fetching current user data:', error);
        // Handle error, such as redirecting to login page
    });

    // Form submission handler
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const review = reviewInput.value.trim();
        if (!review) {
            alert('Please enter a review');
            return;
        }

        const url = `http://localhost:8000/reviews/`;
        const body = JSON.stringify({ isbn, review });

        fetch(url, {
            method: 'POST', // Always POST to add or update
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to submit review');
            }
            return response.json();
        })
        .then(data => {
            alert(data.message || 'Review submitted successfully');
            window.location.href = `/reviews.html?isbn=${isbn}`;
        })
        .catch(error => {
            console.error('Error submitting review:', error);
            alert('Failed to submit review.');
        });
    });
});