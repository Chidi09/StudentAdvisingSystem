// frontend/js/resources.js
document.addEventListener('DOMContentLoaded', () => {
    console.log("Resources Page DOM loaded.");

    const token = localStorage.getItem('accessToken'); // Check if user is logged in
    const logoutButton = document.getElementById('logout-button');
    const navLinksContainer = document.querySelector('.dashboard-nav .nav-links'); // To customize nav

    // --- THEME TOGGLE LOGIC ---
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const bodyElement = document.body;

    function applyCurrentTheme() {
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            if (bodyElement) bodyElement.classList.add('dark-mode');
            if (themeToggleButton) themeToggleButton.textContent = '☀️';
        } else {
            if (bodyElement) bodyElement.classList.remove('dark-mode');
            if (themeToggleButton) themeToggleButton.textContent = '🌙';
        }
    }
    
    if (themeToggleButton && bodyElement) {
        applyCurrentTheme();
        themeToggleButton.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            let newTheme = bodyElement.classList.contains('dark-mode') ? 'dark' : 'light';
            themeToggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', newTheme);
        });
    }

    // --- LOGOUT & NAV CUSTOMIZATION ---
    if (token) {
        if (logoutButton) {
            logoutButton.style.display = 'inline-block'; // Show logout if logged in
            logoutButton.addEventListener('click', (event) => {
                event.preventDefault();
                localStorage.clear();
                window.location.href = 'index.html'; // Go to login page
            });
        }
        // Customize nav links if user is logged in
        const userType = localStorage.getItem('userType');
        if (navLinksContainer) {
            let dashboardLink = 'index.html'; // Default
            if (userType === 'student') dashboardLink = 'student/dashboard.html';
            else if (userType === 'lecturer') dashboardLink = 'lecturer/dashboard.html';
            
            navLinksContainer.innerHTML = `
                <a href="${dashboardLink}">Dashboard</a>
                <a href="resources.html" class="active">Resources</a>
                ${userType ? `<a href="${userType}/profile.html">My Profile</a>` : ''}
            `;
        }

    } else {
        if (logoutButton) logoutButton.style.display = 'none';
        if (navLinksContainer) { // Simpler nav for non-logged-in users
             navLinksContainer.innerHTML = `
                <a href="index.html">Login</a>
                <a href="resources.html" class="active">Resources</a>
            `;
        }
    }

    fetchAllResources();
});

let allFetchedResources = []; // To store all resources for client-side filtering

async function fetchAllResources() {
    console.log("Fetching all advising resources...");
    const resourcesUl = document.getElementById('resources-ul');
    const categoryFilter = document.getElementById('category-filter');

    if (!resourcesUl || !categoryFilter) {
        console.error("Required elements for resources display not found.");
        if (resourcesUl) resourcesUl.innerHTML = '<li>Error: Page structure incomplete.</li>';
        return;
    }
    resourcesUl.innerHTML = '<li><em>Loading resources...</em></li>';

    try {
        const response = await fetch('http://localhost:5000/api/resources'); // New API endpoint
        if (!response.ok) {
            let errorMsg = `HTTP error ${response.status}`;
            try { const errorData = await response.json(); errorMsg = errorData.message || errorMsg; } catch (e) {}
            throw new Error(errorMsg);
        }
        const data = await response.json();

        if (data.success && Array.isArray(data.resources)) {
            allFetchedResources = data.resources; // Store for filtering
            populateCategories(allFetchedResources, categoryFilter);
            displayResources(allFetchedResources, resourcesUl); // Display all initially
            
            categoryFilter.addEventListener('change', (event) => {
                const selectedCategory = event.target.value;
                const filteredResources = (selectedCategory === 'all') 
                    ? allFetchedResources 
                    : allFetchedResources.filter(res => res.category === selectedCategory);
                displayResources(filteredResources, resourcesUl);
            });

        } else {
            console.error("API reported failure or invalid resources data:", data.message);
            resourcesUl.innerHTML = `<li>Error: ${data.message || 'Could not load resources.'}</li>`;
        }
    } catch (error) {
        console.error("Network error fetching resources:", error);
        resourcesUl.innerHTML = `<li>Network error: ${error.message}. Please try again.</li>`;
    }
}

function populateCategories(resources, filterDropdown) {
    const categories = new Set(); // Use a Set to get unique categories
    resources.forEach(res => {
        if (res.category) categories.add(res.category);
    });

    // Clear existing options except "All Categories"
    while (filterDropdown.options.length > 1) {
        filterDropdown.remove(1);
    }

    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        filterDropdown.appendChild(option);
    });
}

function displayResources(resourcesToDisplay, ulElement) {
    ulElement.innerHTML = ''; // Clear current list

    if (resourcesToDisplay.length > 0) {
        resourcesToDisplay.forEach(resource => {
            const li = document.createElement('li');
            li.className = 'resource-item'; // Add a class for potential specific styling

            const titleLink = document.createElement('a');
            titleLink.href = resource.url || '#';
            titleLink.textContent = resource.title || 'Unnamed Resource';
            titleLink.className = 'resource-title';
            if (resource.url && resource.url !== '#') {
                titleLink.target = '_blank'; // Open external links in new tab
            }
            
            const descriptionP = document.createElement('p');
            descriptionP.className = 'resource-description';
            descriptionP.textContent = resource.description || 'No description available.';
            
            const categorySpan = document.createElement('span');
            categorySpan.className = 'resource-category';
            categorySpan.textContent = `Category: ${resource.category || 'General'}`;

            li.appendChild(titleLink);
            li.appendChild(descriptionP);
            li.appendChild(categorySpan);
            ulElement.appendChild(li);
        });
    } else {
        ulElement.innerHTML = '<li>No resources found matching your criteria.</li>';
    }
}

// End of resources.js
// Note: Ensure to include this script in your HTML file and link it properly.