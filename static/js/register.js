document.addEventListener('DOMContentLoaded', function() {
    const registerBtn = document.getElementById('registerBtn');
    const roleField = document.getElementById('registerRole');
    const adminSecretField = document.getElementById('adminSecretField');

    // Show/hide the admin secret password field based on the selected role
    roleField.addEventListener('change', function() {
        if (roleField.value === 'admin') {
            adminSecretField.style.display = 'block';
        } else {
            adminSecretField.style.display = 'none';
        }
    });

    if (registerBtn) {
        registerBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const usernameField = document.getElementById('registerUsername');
            const passwordField = document.getElementById('registerPassword');
            const adminSecretPasswordField = document.getElementById('adminSecretPassword');
            const username = usernameField.value.trim();
            const password = passwordField.value.trim();
            const role = roleField.value;
            const adminSecretPassword = adminSecretPasswordField ? adminSecretPasswordField.value.trim() : '';
            const adminSecretRequired = role === 'admin';

            // Define your secret admin password here
            const adminSecret = 'mySecretAdminPassword';

            // Check if username, password, and admin secret password (if required) are valid
            if (username && password && (!adminSecretRequired || adminSecretPassword === adminSecret)) {
                if (adminSecretRequired && adminSecretPassword !== adminSecret) {
                    document.getElementById('registerResponse').textContent = 'Invalid admin secret password.';
                    return;
                }

                // Send the registration data to the backend
                fetch('http://localhost:8000/register/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ username: username, password: password, role: role })
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
                    if (adminSecretPasswordField) {
                        adminSecretPasswordField.value = '';
                    }
                    roleField.value = 'regular';  // Reset to default role
                    adminSecretField.style.display = 'none';  // Hide secret field
                })
                .catch(error => {
                    console.error('Registration error:', error);
                    document.getElementById('registerResponse').textContent = error.message;
                });
            } else {
                document.getElementById('registerResponse').textContent = 'All fields are required.';
            }
        });
    }
});