// student/courses.js

document.addEventListener('DOMContentLoaded', async () => {
    const backendBaseUrl = 'http://127.0.0.1:5000'; // Your Flask backend URL

    // Get elements to display data
    const cgpaDisplay = document.getElementById('cgpa-display');
    const outstandingCoursesCount = document.getElementById('outstanding-courses-count');
    const enrolledCoursesTableBody = document.getElementById('enrolled-courses-table-body');
    const outstandingCoursesTableBody = document.getElementById('outstanding-courses-table-body');
    const userNameDisplay = document.getElementById('user-name');

    // Theme Toggle Elements
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const bodyElement = document.body;

    // Function to apply theme on page load
    function applyTheme() {
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            bodyElement.classList.add('dark-mode');
            if(themeToggleButton) themeToggleButton.textContent = '☀️';
        } else {
            bodyElement.classList.remove('dark-mode');
            if(themeToggleButton) themeToggleButton.textContent = '🌙';
        }
    }
    applyTheme(); // Apply theme immediately on DOMContentLoaded

    // Add event listener for theme toggle button
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            let newTheme = bodyElement.classList.contains('dark-mode') ? 'dark' : 'light';
            themeToggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', newTheme);
            console.log("Theme toggled. Current theme:", newTheme);
        });
    } else {
        console.warn("Theme toggle button (#theme-toggle-button) not found on courses page.");
    }


    // Function to get JWT token from localStorage
    const getAuthToken = () => localStorage.getItem('access_token');

    // Function to handle logout (already in script.js, but good to have a local reference)
    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_type');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_id');
        window.location.href = '../index.html'; // Redirect to login page
    };

    // Attach logout event listener if not already handled by script.js
    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    // Display user name from local storage
    const storedUserName = localStorage.getItem('user_name');
    if (userNameDisplay && storedUserName) {
        userNameDisplay.textContent = storedUserName;
    }

    // Function to fetch and display courses overview data
    const fetchCoursesOverview = async () => {
        const token = getAuthToken();
        if (!token) {
            alert('You are not logged in. Please log in to view this page.');
            handleLogout(); // Redirect to login
            return;
        }

        try {
            const response = await fetch(`${backendBaseUrl}/api/student/courses-overview`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Courses Overview Data:', data); // Debugging

                // Update CGPA and Outstanding Courses Count
                cgpaDisplay.textContent = data.cgpa !== undefined ? data.cgpa : '--';
                outstandingCoursesCount.textContent = data.outstanding_courses_count !== undefined ? data.outstanding_courses_count : '--';

                // Populate Enrolled Courses Table
                enrolledCoursesTableBody.innerHTML = ''; // Clear loading message
                if (data.enrolled_courses && data.enrolled_courses.length > 0) {
                    data.enrolled_courses.forEach(course => {
                        const row = enrolledCoursesTableBody.insertRow();
                        row.insertCell(0).textContent = course.code;
                        row.insertCell(1).textContent = course.title;
                        row.insertCell(2).textContent = course.units;
                        row.insertCell(3).textContent = course.grade || 'N/A';
                        row.insertCell(4).textContent = course.semester || 'N/A';
                    });
                } else {
                    enrolledCoursesTableBody.innerHTML = '<tr><td colspan="5">No enrolled courses found.</td></tr>';
                }

                // Populate Outstanding Courses Table
                outstandingCoursesTableBody.innerHTML = ''; // Clear loading message
                if (data.outstanding_courses && data.outstanding_courses.length > 0) {
                    data.outstanding_courses.forEach(course => {
                        const row = outstandingCoursesTableBody.insertRow();
                        row.insertCell(0).textContent = course.code;
                        row.insertCell(1).textContent = course.title;
                        row.insertCell(2).textContent = course.units;
                        row.insertCell(3).textContent = course.level || 'N/A';
                        row.insertCell(4).textContent = course.semester || 'N/A';
                    });
                } else {
                    outstandingCoursesTableBody.innerHTML = '<tr><td colspan="5">No outstanding courses found.</td></tr>';
                }

            } else if (response.status === 401 || response.status === 403) {
                alert('Session expired or unauthorized. Please log in again.');
                handleLogout();
            } else {
                const errorData = await response.json();
                console.error('Failed to fetch courses overview:', errorData.message);
                alert(`Error: ${errorData.message || 'Failed to load courses data.'}`);
                enrolledCoursesTableBody.innerHTML = '<tr><td colspan="5">Failed to load enrolled courses.</td></tr>';
                outstandingCoursesTableBody.innerHTML = '<tr><td colspan="5">Failed to load outstanding courses.</td></tr>';
            }
        } catch (error) {
            console.error('Network error or unexpected issue:', error);
            alert('A network error occurred. Please check your connection or try again later.');
            enrolledCoursesTableBody.innerHTML = '<tr><td colspan="5">Error loading data.</td></tr>';
            outstandingCoursesTableBody.innerHTML = '<tr><td colspan="5">Error loading data.</td></tr>';
        }
    };

    // Fetch data when the page loads
    fetchCoursesOverview();
});
