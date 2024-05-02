document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const responseMessage = document.getElementById('responseMessage');

    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const username = document.getElementById('usernameInput').value.trim();
        const password = document.getElementById('passwordInput').value.trim();

        fetch('http://localhost:8000/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ username, password })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Invalid credentials');
                }
                return response.json();
            })
            .then(data => {
                localStorage.setItem('token', data.access_token);
                responseMessage.textContent = 'Login successful!';
                window.location.href = '/browse';
            })
            .catch(error => {
                responseMessage.textContent = error.message;
            });
    });

    // // Hide or show elements based on login status
    // const token = localStorage.getItem('token');
    // if (token) {
    //     document.getElementById('logoutLink').style.display = 'inline';
    // }
});