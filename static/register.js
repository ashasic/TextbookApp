document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('registerBtn');
    if (registerBtn) {
        registerBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const username = document.getElementById('registerUsername').value.trim();
            const password = document.getElementById('registerPassword').value.trim();
            if (username && password) {
                fetch('http://localhost:8000/register/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username, password: password })
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        response.json().then(data => {
                            throw new Error(data.detail || 'Failed to register');
                        });
                    }
                })
                .then(data => {
                    document.getElementById('registerResponse').textContent = 'Registration successful!';
                })
                .catch(error => {
                    console.error('Registration error:', error);
                    document.getElementById('registerResponse').textContent = error.message;
                });
            } else {
                document.getElementById('registerResponse').textContent = 'Both fields are required.';
            }
        });
    }
});
