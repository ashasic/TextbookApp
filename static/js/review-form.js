document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('reviewForm');
    const isbnInput = document.getElementById('isbn');
    const reviewInput = document.getElementById('review');
    const params = new URLSearchParams(window.location.search);
    const isbn = params.get('isbn');
    const token = localStorage.getItem('token'); // JWT token from local storage

    if (!isbn) {
        alert('ISBN not specified');
        return;
    }

    // Set the ISBN hidden field value
    isbnInput.value = isbn;

    // Check if the review already exists
    fetch(`/user`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch current user data');
        }
        return response.json();
    })
    .then(userData => {
        const user = userData.username;

        fetch(`http://localhost:8000/reviews/${isbn}/${user}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.status === 404) {
                console.log('No existing review found, assuming a new review');
                return null;
            }
            if (!response.ok) {
                throw new Error('Failed to check review status');
            }
            return response.json();
        })
        .then(data => {
            if (data) {
                reviewInput.value = data.review; // Pre-fill review input
            }
        })
        .catch(error => {
            console.error('Error checking review status:', error);
            alert('Error checking review status.');
        });
    })
    .catch(error => {
        console.error('Error fetching current user data:', error);
        alert('Please log in to continue.');
        window.location.href = '/login.html'; // Redirect to login
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