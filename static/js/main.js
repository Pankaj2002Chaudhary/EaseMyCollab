// Store token
function setToken(token) {
    localStorage.setItem("token", token);
}

// Get token
function getToken() {
    return localStorage.getItem("token");
}

// Check login
function isLoggedIn() {
    return getToken() !== null;
}

// Logout
function logout() {
    localStorage.removeItem("token");
    alert("Logged out");
    window.location.href = "/";
}

// Navbar logic
function loadNavbar() {
    let nav = document.getElementById("nav-right");
    if (!nav) return;

    if (localStorage.getItem("token")) {
        nav.innerHTML = `
            <button class="btn btn-light me-2">Profile</button>
            <button class="btn btn-danger" onclick="logout()">Logout</button>
        `;
    } else {
        nav.innerHTML = `
            <a href="/login/" class="btn btn-light me-2">Login</a>
            <a href="/register/" class="btn btn-primary">Register</a>
        `;
    }
}

// Run after page loads
document.addEventListener("DOMContentLoaded", loadNavbar);

function applyCampaign(id) {
    let token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        window.location.href = "/login/";
        return;
    }

    fetch(`http://127.0.0.1:8000/api/apply/${id}/`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
    });
}