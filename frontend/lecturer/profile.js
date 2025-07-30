// frontend/lecturer/profile.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("Lecturer Profile DOM loaded.");

    const token = localStorage.getItem('accessToken');
    const userType = localStorage.getItem('userType'); // Get userType to verify

    if (!token || userType !== 'lecturer') { // Check for token AND correct userType
        console.error('No valid lecturer session found. Redirecting to login.');
        localStorage.clear(); // Clear potentially incorrect session info
        window.location.href = '../index.html'; // Adjust path as necessary
        return;
    }

    // Setup Logout Button
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', (event) => {
            event.preventDefault();
            localStorage.clear();
            console.log("Profile: Logged out, redirecting.");
            window.location.href = '../index.html'; 
        });
    }

    // Setup Theme Toggle Button
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const bodyElement = document.body;
    if (themeToggleButton && bodyElement) {
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            bodyElement.classList.add('dark-mode');
            themeToggleButton.textContent = '☀️';
        } else {
            themeToggleButton.textContent = '🌙';
        }
        themeToggleButton.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            let newTheme = bodyElement.classList.contains('dark-mode') ? 'dark' : 'light';
            themeToggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', newTheme);
        });
    }

    fetchLecturerProfileData(token);
});

// Helper function to safely set text content
function setTextContent(elementId, text, defaultText = '[N/A]') {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = (text === null || text === undefined || String(text).trim() === "") ? defaultText : String(text);
    } else {
        console.warn(`Element with ID '${elementId}' not found for lecturer profile page.`);
    }
}

async function fetchLecturerProfileData(token) {
    console.log("Fetching lecturer profile data...");
    // We reuse the /api/lecturer/data endpoint which should contain all necessary info
    const profileDataUrl = 'http://localhost:5000/api/lecturer/data'; 

    try {
        const response = await fetch(profileDataUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const mainProfileArea = document.getElementById('lecturer-profile-card'); 

        if (!response.ok) {
            let errorMsg = `HTTP error ${response.status}`;
            try {
                const errorDataJson = await response.json();
                errorMsg = errorDataJson.message || errorMsg;
            } catch (e) { /* ignore if error response not json */ }
            
            console.error(`Error fetching lecturer profile data: ${errorMsg}`);
            if (mainProfileArea) mainProfileArea.innerHTML = `<p class="error-message">Could not load profile: ${errorMsg}</p>`;
            
            if (response.status === 401 || response.status === 422) { // Unauthorized or Unprocessable Entity
                localStorage.clear();
                window.location.href = '../index.html'; // Redirect to login
            }
            return;
        }

        const data = await response.json();

        if (data.success && data.lecturer_info) { // Check for success and lecturer_info
            console.log("Parsed lecturer profile data:", data.lecturer_info);
            populateLecturerProfilePage(data.lecturer_info);
        } else {
            console.error("Backend reported failure or missing lecturer_info in profile data:", data.message);
            if (mainProfileArea) mainProfileArea.innerHTML = `<p class="error-message">Could not load profile: ${data.message || 'Lecturer information not found.'}</p>`;
        }
    } catch (error) {
        console.error("Network error during lecturer profile data fetching:", error);
        const mainProfileArea = document.getElementById('lecturer-profile-card');
        if (mainProfileArea) mainProfileArea.innerHTML = `<p class="error-message">Error loading profile data. Please check connection and try again.</p>`;
    }
}

function populateLecturerProfilePage(lecturerInfo) { // Takes lecturer_info directly
    console.log("Populating lecturer profile page with:", lecturerInfo);

    setTextContent('profile-lecturer-fullname', lecturerInfo.name);
    setTextContent('profile-lecturer-email', lecturerInfo.email);
    setTextContent('profile-lecturer-dept', lecturerInfo.department);
    setTextContent('profile-lecturer-office', lecturerInfo.office_location); // Matches key from API
    
    console.log("Lecturer profile page populated.");
}