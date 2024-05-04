document.addEventListener('DOMContentLoaded', function () {
    const addReviewBtn = document.getElementById('addReviewBtn');
    const backToBrowseBtn = document.getElementById('backToBrowseBtn');
    const reviewsList = document.getElementById('reviewsList');
    const isbn = new URLSearchParams(window.location.search).get('isbn');
    const token = localStorage.getItem('token'); // Fetch the token from local storage

    if (!isbn) {
        alert('ISBN not specified');
        return;
    }

    // Redirect to the review form with the ISBN as a query parameter
    addReviewBtn.addEventListener('click', function () {
        window.location.href = `/review-form.html?isbn=${isbn}`;
    });

    // Go back to the browse page
    backToBrowseBtn.addEventListener('click', function () {
        window.location.href = '/browse.html';
    });

    // Load reviews for a specific textbook
    function loadReviews() {
        fetch(`http://localhost:8000/reviews/${isbn}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load reviews');
            }
            return response.json();
        })
        .then(data => {
            reviewsList.innerHTML = '';
            if (data.reviews && data.reviews.length) {
                data.reviews.forEach(review => {
                    const reviewElement = document.createElement('div');
                    reviewElement.className = 'review';
                    reviewElement.innerHTML = `
                        <p>User: ${review.user}</p>
                        <p>Review: ${review.review}</p>
                        <button class="editReviewBtn" data-id="${review.id}">Edit</button>
                        <button class="deleteReviewBtn" data-id="${review.id}">Delete</button>
                    `;
                    reviewsList.appendChild(reviewElement);

                    // Attach event listeners to edit and delete buttons
                    reviewElement.querySelector('.editReviewBtn').addEventListener('click', () => editReview(review.id));
                    reviewElement.querySelector('.deleteReviewBtn').addEventListener('click', () => deleteReview(review.id));
                });
            } else {
                reviewsList.textContent = 'No reviews found.';
            }
        })
        .catch(error => {
            console.error('Error fetching reviews:', error);
            reviewsList.textContent = 'Failed to load reviews.';
        });
    }

    // Redirect to the review form for editing an existing review
    function editReview(reviewId) {
        window.location.href = `/review-form.html?isbn=${isbn}&id=${reviewId}`;
    }

    // Delete a specific review
    function deleteReview(reviewId) {
        if (confirm('Are you sure you want to delete this review?')) {
            fetch(`http://localhost:8000/reviews/${reviewId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to delete review');
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);
                loadReviews(); // Reload the reviews after deletion
            })
            .catch(error => {
                console.error('Error deleting review:', error);
                alert('Failed to delete review.');
            });
        }
    }

    loadReviews(); // Initial load of reviews
});