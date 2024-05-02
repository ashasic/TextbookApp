document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('registerBtn');
    if (registerBtn) {
        registerBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const usernameField = document.getElementById('registerUsername');
            const passwordField = document.getElementById('registerPassword');
            const username = usernameField.value.trim();
            const password = passwordField.value.trim();
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
                    usernameField.value = '';
                    passwordField.value = '';
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
