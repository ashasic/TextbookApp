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

    // Load review for editing, if ID is specified
    const reviewId = params.get('id');
    if (reviewId) {
        fetch(`http://localhost:8000/reviews/${isbn}`, {
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
            const review = data.reviews.find(r => r._id === reviewId);
            if (review) {
                reviewInput.value = review.review;
            }
        })
        .catch(error => {
            console.error('Error loading review:', error);
            alert('Failed to load review');
        });
    }

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