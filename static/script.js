document.getElementById('addTextbookBtn').addEventListener('click', function() {
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
            document.getElementById('responseMessage').textContent = data.message + ': ' + JSON.stringify(data.data);
        })
        .catch(error => {
            document.getElementById('responseMessage').textContent = 'Error adding/updating textbook: ' + error;
        });
    } else {
        document.getElementById('responseMessage').textContent = 'Please enter a valid ISBN.';
    }
});
