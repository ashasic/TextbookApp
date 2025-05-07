document.addEventListener('DOMContentLoaded', function () {
    const addReviewBtn = document.getElementById('addReviewBtn');
    const backToBrowseBtn = document.getElementById('backToBrowseBtn');
    const reviewsList = document.getElementById('reviewsList');
    const isbn = new URLSearchParams(window.location.search).get('isbn');
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const isAdmin = user.role === 'admin';
    const currentUser = user.username;

    if (!isbn) {
        alert('ISBN not specified');
        return;
    }

    if (!token) {
        alert("You must be logged in to view or leave reviews.");
        window.location.href = '/login';
        return;
    }

    addReviewBtn.addEventListener('click', function () {
        window.location.href = `/review-form.html?isbn=${isbn}`;
    });

    backToBrowseBtn.addEventListener('click', function () {
        window.location.href = '/browse';
    });

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
                    const canEdit = isAdmin || review.user === currentUser;

                    const reviewElement = document.createElement('div');
                    reviewElement.className = 'review-entry';
                    reviewElement.innerHTML = `
                        <p><strong>${review.user}</strong></p>
                        <p class="review-meta">${review.review}</p>
                        ${canEdit ? `
                        <div class="review-actions">
                            <button class="editReviewBtn" data-user="${review.user}">Edit</button>
                            <button class="deleteReviewBtn" data-user="${review.user}">Delete</button>
                        </div>
                        ` : ''}
                    `;
                    reviewsList.appendChild(reviewElement);

                    if (canEdit) {
                        reviewElement.querySelector('.editReviewBtn').addEventListener('click', () => editReview(review.user));
                        reviewElement.querySelector('.deleteReviewBtn').addEventListener('click', () => deleteReview(isbn, review.user));
                    }
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

    function editReview(user) {
        window.location.href = `/review-form.html?isbn=${isbn}&user=${user}`;
    }

    function deleteReview(isbn, user) {
        if (confirm('Are you sure you want to delete this review?')) {
            fetch(`http://localhost:8000/reviews/${isbn}/${user}`, {
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
                loadReviews();
            })
            .catch(error => {
                console.error('Error deleting review:', error);
                alert('Failed to delete review.');
            });
        }
    }

    loadReviews();
});