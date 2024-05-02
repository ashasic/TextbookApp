document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('token');
    if (token) {
        document.getElementById('loginLink').style.display = 'none';
        document.getElementById('registerLink').style.display = 'none';
        document.getElementById('logoutLink').style.display = 'inline';
    } else {
        document.getElementById('logoutLink').style.display = 'none';
    }

    document.getElementById('logoutLink').addEventListener('click', function () {
        localStorage.removeItem('token');
        window.location.href = '/login';
    });
});