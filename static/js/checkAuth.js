document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('token');

    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutLink = document.getElementById('logoutLink');
    const browseLink = document.getElementById('browseLink');
    const dashboardLink = document.getElementById('dashboardLink');

    if (token) {
        loginLink.style.display = 'none';
        registerLink.style.display = 'none';
        logoutLink.style.display = 'inline-block';
    } else {
        logoutLink.style.display = 'none';
        if (browseLink) {
            browseLink.addEventListener('click', function (event) {
                event.preventDefault();
                alert("Please log in to access Browse.");
                window.location.href = '/login';
            });
        }
        if (dashboardLink) {
            dashboardLink.addEventListener('click', function (event) {
                event.preventDefault();
                alert("Please log in to access your Dashboard.");
                window.location.href = '/login';
            });
        }

        // Block access to protected pages
        const protectedPaths = ['/reviews.html', '/review-form.html', '/dashboard'];
        if (protectedPaths.some(p => window.location.pathname.startsWith(p))) {
            alert("You must be logged in to view this page.");
            window.location.href = "/login";
        }
    }

    logoutLink.addEventListener('click', function () {
        localStorage.removeItem('token');
        window.location.href = '/login';
    });
});