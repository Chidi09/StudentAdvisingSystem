// /frontend/lecturer/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("Lecturer Dashboard DOM loaded.");
    window.allAdviseesData = {}; 

    const token = localStorage.getItem('accessToken');
    if (!token) {
        console.error('No access token found. Redirecting to login.');
        window.location.href = '../index.html';
        return;
    }

    setupCommonButtons(); 
    
    const addNoteForm = document.getElementById('add-note-form');
    if (addNoteForm) {
        addNoteForm.addEventListener('submit', handleAddNoteFormSubmit);
    } else {
        console.warn("Add Note Form (#add-note-form) not found.");
    }

    const contactGuardianForm = document.getElementById('contactGuardianForm');
    if (contactGuardianForm) {
        contactGuardianForm.addEventListener('submit', handleContactGuardianFormSubmit);
    } else {
        console.warn("Contact Guardian Form (#contactGuardianForm) not found.");
    }
    
    fetchLecturerData(token);
});

function setupCommonButtons() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        console.log("Logout button element found:", logoutButton);
        logoutButton.addEventListener('click', (event) => { 
            event.preventDefault(); 
            logoutUser();
        });
    } else {
        console.warn("Logout button (#logout-button) not found.");
    }
    
    const themeToggleButton = document.getElementById('theme-toggle-button');
    const bodyElement = document.body; 
    if (themeToggleButton && bodyElement) { 
        console.log("Theme toggle button element found:", themeToggleButton);
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'dark') {
            bodyElement.classList.add('dark-mode');
            themeToggleButton.textContent = '☀️'; 
        } else {
            bodyElement.classList.remove('dark-mode'); 
            themeToggleButton.textContent = '🌙'; 
        }
        themeToggleButton.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            let newTheme = bodyElement.classList.contains('dark-mode') ? 'dark' : 'light';
            themeToggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', newTheme);
            console.log("Theme toggled to:", newTheme);
        });
    } else { 
        if (!themeToggleButton) console.warn("Theme toggle button (#theme-toggle-button) not found.");
        if (!bodyElement) console.warn("Body element not found for theme toggle.");
    }

    const closeResultsBtn = document.getElementById('close-advisee-results-btn');
    if (closeResultsBtn) {
        closeResultsBtn.addEventListener('click', () => closeModal('view-advisee-results-section'));
    }
    const closeNotesBtn = document.getElementById('close-advisee-notes-btn');
    if(closeNotesBtn) {
        closeNotesBtn.addEventListener('click', () => closeModal('view-notes-section'));
    }
}

async function fetchLecturerData(token) {
    try {
        console.log("Fetching initial dashboard data...");
        const response = await fetch('http://localhost:5000/api/lecturer/data', { // Absolute URL
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            let errorMsg = `HTTP error ${response.status}`;
            try { const errorData = await response.json(); errorMsg = errorData.message || errorMsg; } catch (e) {}
            throw new Error(errorMsg); 
        }
        const lecturerData = await response.json();
        console.log("Parsed lecturer data (raw):", JSON.parse(JSON.stringify(lecturerData)));
        if (lecturerData.success) {
            populateLecturerDashboard(lecturerData);
        } else {
            console.error("API reported failure fetching lecturer data:", lecturerData.message);
            const mainContent = document.querySelector('.dashboard-main');
            if (mainContent) mainContent.innerHTML = `<p class="error-message">Could not load lecturer data: ${lecturerData.message || "Unknown server error."}</p>`;
        }
    } catch (error) { 
        console.error('Error fetching lecturer data (in fetchLecturerData catch):', error.message);
        handleFetchError(error); 
    }
}

function setTextContent(elementId, text, defaultText = '[N/A]') {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = (text === null || text === undefined || String(text).trim() === "") ? defaultText : String(text);
    } else {
        // console.warn(`Element with ID '${elementId}' not found for setTextContent.`);
    }
}

function populateLecturerDashboard(data) {
    console.log("populateLecturerDashboard CALLED with data:", JSON.parse(JSON.stringify(data))); 
    const lecturerInfo = data.lecturer_info || {};
    const advisees = data.advisees || [];
    const resources = data.resources || [];

    window.allAdviseesData = {}; 
    advisees.forEach(adv => window.allAdviseesData[adv.id] = adv); 

    setTextContent('welcome-lecturer-name', lecturerInfo.name, '[Lecturer]');
    setTextContent('lecturer-name', lecturerInfo.name);
    setTextContent('lecturer-email', lecturerInfo.email); 
    setTextContent('lecturer-dept', lecturerInfo.department); 
    setTextContent('lecturer-office', lecturerInfo.office_location); 

    const adviseesTableBody = document.querySelector('#advisees-table tbody');
    if (adviseesTableBody) {
        adviseesTableBody.innerHTML = ''; 
        if (advisees.length > 0) {
            advisees.forEach((student) => {
                let row = adviseesTableBody.insertRow();
                row.insertCell().textContent = student.matric_number || 'N/A';
                row.insertCell().textContent = student.name || 'N/A';
                row.insertCell().textContent = student.email || 'N/A';
                row.insertCell().textContent = student.degree || 'N/A'; 
                row.insertCell().textContent = student.gpa !== null && student.gpa !== undefined ? student.gpa.toString() : 'N/A';
                let actionsCell = row.insertCell();
                actionsCell.innerHTML = `
                    <button class="action-btn view-details-btn" data-student-id="${student.id}" onclick="openAdviseeDetailsModal(this)">Details</button>
                    <button class="action-btn view-results-btn" data-student-id="${student.id}" data-student-name="${student.name}" onclick="viewAdviseeResults(this)">Results</button>
                    <button class="action-btn note-btn" data-student-id="${student.id}" data-student-name="${student.name}" onclick="prepareAddNoteForAdvisee(this)">Add Note</button>
                    <button class="action-btn view-notes-btn" data-student-id="${student.id}" data-student-name="${student.name}" onclick="fetchAndDisplayNotesForAdvisee(this)">View Notes</button>
                    <button class="action-btn contact-guardian-btn" data-student-id="${student.id}" onclick="openContactGuardianModal(this)">Contact Guardian</button>
                `;
            });
        } else {
            adviseesTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No advisees assigned to you.</td></tr>';
        }
    } else {
        console.error("Advisees table body ('#advisees-table tbody') NOT FOUND!");
    }

    const resourceListUl = document.getElementById('resource-list');
    if (resourceListUl) { 
        resourceListUl.innerHTML = '';
        if (resources && resources.length > 0) {
            resources.forEach(resource => { /* ... populate list ... */ });
        } else {
            resourceListUl.innerHTML = '<li>No resources available.</li>';
        }
    }
    console.log("Finished populating lecturer dashboard.");
}

function openAdviseeDetailsModal(buttonElement) {
    const studentId = buttonElement.getAttribute('data-student-id');
    const advisee = window.allAdviseesData[studentId];
    if (!advisee) { alert("Could not find details for this advisee."); return; }
    setTextContent('modal-advisee-name', advisee.name);
    setTextContent('modal-advisee-matric', advisee.matric_number);
    setTextContent('modal-advisee-email', advisee.email);
    setTextContent('modal-advisee-degree', advisee.degree);
    setTextContent('modal-advisee-gpa', advisee.gpa !== null && advisee.gpa !== undefined ? advisee.gpa.toString() : 'N/A');
    setTextContent('modal-guardian-name', advisee.guardian_name);
    setTextContent('modal-guardian-email', advisee.guardian_email);
    setTextContent('modal-guardian-phone', advisee.guardian_phone);
    setTextContent('modal-guardian-relationship', advisee.guardian_relationship);
    const modal = document.getElementById('adviseeDetailsModal');
    if (modal) modal.style.display = 'block';
}

function openContactGuardianModal(buttonElement) {
    const studentId = buttonElement.getAttribute('data-student-id');
    const advisee = window.allAdviseesData[studentId];
    if (!advisee) { alert("Could not find advisee data to contact guardian."); return; }
    if (!advisee.guardian_email) { alert(`${advisee.name || 'This student'} does not have a registered guardian email.`); return; }
    setTextContent('modal-contact-advisee-name', advisee.name);
    setTextContent('modal-contact-guardian-email-display', advisee.guardian_email);
    const adviseeIdInput = document.getElementById('contact-advisee-id');
    if (adviseeIdInput) adviseeIdInput.value = studentId;
    const guardianEmailInput = document.getElementById('contact-guardian-email-hidden');
    if (guardianEmailInput) guardianEmailInput.value = advisee.guardian_email;
    const subjectInput = document.getElementById('contact-subject');
    if (subjectInput) subjectInput.value = `Regarding your ward, ${advisee.name || 'Student'}`;
    const messageBodyInput = document.getElementById('contact-message-body');
    if (messageBodyInput) messageBodyInput.value = ''; 
    const isUrgentCheckbox = document.getElementById('contact-is-urgent');
    if (isUrgentCheckbox) isUrgentCheckbox.checked = false;
    const statusDiv = document.getElementById('contact-guardian-status');
    if (statusDiv) { statusDiv.textContent = ''; statusDiv.className = 'message-display'; }
    const modal = document.getElementById('contactGuardianModal');
    if (modal) modal.style.display = 'block';
}

async function handleContactGuardianFormSubmit(event) {
    event.preventDefault();
    const token = localStorage.getItem('accessToken');
    const statusDiv = document.getElementById('contact-guardian-status');
    if (!statusDiv) { console.error("Status div for contact guardian form not found."); return; }
    statusDiv.className = 'message-display visible'; 

    if (!token) {
        statusDiv.textContent = "Authentication error."; statusDiv.className = 'message-display error visible'; return;
    }
    const adviseeId = document.getElementById('contact-advisee-id').value;
    const subject = document.getElementById('contact-subject').value;
    const messageBody = document.getElementById('contact-message-body').value;
    const isUrgent = document.getElementById('contact-is-urgent').checked;

    if (!adviseeId) { statusDiv.textContent = "Error: Advisee ID not set."; statusDiv.className = 'message-display error visible'; return; }
    if (!subject.trim()) { statusDiv.textContent = "Subject cannot be empty."; statusDiv.className = 'message-display error visible'; return; }
    if (!messageBody.trim()) { statusDiv.textContent = "Message body cannot be empty."; statusDiv.className = 'message-display error visible'; return; }

    statusDiv.textContent = "Sending email..."; statusDiv.style.color = ''; 

    const payload = { message_body: messageBody, subject: subject, is_urgent: isUrgent };
    console.log("Sending contact guardian request for advisee ID:", adviseeId, "Payload:", payload);

    try {
        // --- CORRECTED FETCH URL ---
        const response = await fetch(`http://localhost:5000/api/advisees/${adviseeId}/contact-guardian`, {
        // --- END CORRECTION ---
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        console.log("Contact guardian API response:", result);

        if (response.ok && result.success) {
            statusDiv.textContent = result.message || "Email sent successfully!";
            statusDiv.className = 'message-display success visible';
            setTimeout(() => { closeModal('contactGuardianModal'); document.getElementById('contactGuardianForm').reset(); }, 2500);
        } else {
            statusDiv.textContent = result.message || "Failed to send email.";
            statusDiv.className = 'message-display error visible';
        }
    } catch (error) {
        console.error("Error contacting guardian:", error);
        statusDiv.textContent = "Network error or server issue while contacting guardian.";
        statusDiv.className = 'message-display error visible';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = "none";
}

async function viewAdviseeResults(buttonElement) { /* ... (Keep existing implementation from response #63) ... */ 
    const studentId = buttonElement.getAttribute('data-student-id');
    const studentName = buttonElement.getAttribute('data-student-name');
    const token = localStorage.getItem('accessToken');
    if (!token) { alert("Authentication token not found."); handleFetchError(new Error("Token not found")); return; }
    const resultsSection = document.getElementById('view-advisee-results-section');
    const resultsTableBody = document.querySelector('#advisee-results-table tbody');
    const adviseeNameSpan = document.getElementById('viewing-results-for-advisee-name');
    if (!resultsSection || !resultsTableBody || !adviseeNameSpan) { console.error("UI elements for advisee results display are missing."); return; }
    adviseeNameSpan.textContent = studentName ? studentName : `Student ID: ${studentId}`;
    resultsTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Fetching results...</td></tr>';
    resultsSection.style.display = 'block'; resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
        const response = await fetch(`http://localhost:5000/api/lecturer/advisees/${studentId}/results`, { method: 'GET', headers: { 'Authorization': `Bearer ${token}` }});
        if (!response.ok) { let errorMsg = `HTTP error ${response.status}`; try { const errorData = await response.json(); errorMsg = errorData.message || errorMsg; } catch (e) {} throw new Error(errorMsg); }
        const data = await response.json(); resultsTableBody.innerHTML = ''; 
        if (data.success && data.results) {
            if (data.results.length > 0) {
                data.results.forEach(r => { let row = resultsTableBody.insertRow(); row.insertCell().textContent = r.course_code || 'N/A'; row.insertCell().textContent = r.course_title || 'N/A'; row.insertCell().textContent = r.course_units !== null ? r.course_units : 'N/A'; row.insertCell().textContent = r.semester || 'N/A'; row.insertCell().textContent = r.grade || 'N/A'; row.insertCell().textContent = r.grade_points !== null ? parseFloat(r.grade_points).toFixed(2) : 'N/A'; });
            } else { resultsTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No academic results found for this student.</td></tr>'; }
        } else { resultsTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red;">${data.message || "Could not fetch results."}</td></tr>`; }
    } catch (error) { console.error("Error fetching/displaying advisee results:", error.message); resultsTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red;">${error.message || "Failed to load results."}</td></tr>`; }
}
function prepareAddNoteForAdvisee(buttonElement) { /* ... (Keep existing implementation from response #63) ... */ 
    const studentId = buttonElement.getAttribute('data-student-id');
    const studentName = buttonElement.getAttribute('data-student-name');
    const addNoteSectionDescription = document.querySelector('#add-note-section > p');
    const noteForm = document.getElementById('add-note-form');
    const noteContentTextArea = document.getElementById('note-content');
    const addNoteSection = document.getElementById('add-note-section');
    if (addNoteSectionDescription) addNoteSectionDescription.innerHTML = `Enter note for: <strong>${studentName}</strong> (Student ID: ${studentId})`;
    if (noteForm) noteForm.setAttribute('data-student-id', studentId);
    if (noteContentTextArea) { noteContentTextArea.value = ''; noteContentTextArea.focus(); }
    if (addNoteSection) addNoteSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
async function handleAddNoteFormSubmit(event) { /* ... (Keep existing implementation from response #63) ... */ 
    event.preventDefault(); const token = localStorage.getItem('accessToken'); const studentId = this.getAttribute('data-student-id'); const content = document.getElementById('note-content').value; const statusSpan = document.getElementById('add-note-status');
    if (!statusSpan) { console.error("Status span for add note not found"); return; }
    statusSpan.className = 'message-display'; statusSpan.textContent = ""; 
    if (!token) { statusSpan.textContent = "Authentication error."; statusSpan.className = 'message-display error visible'; return; }
    if (!studentId) { statusSpan.textContent = "Please select an advisee first..."; statusSpan.className = 'message-display error visible'; return; }
    if (!content.trim()) { statusSpan.textContent = "Note content cannot be empty."; statusSpan.className = 'message-display error visible'; return; }
    statusSpan.textContent = "Saving note..."; statusSpan.className = 'message-display visible';
    try {
        const response = await fetch(`http://localhost:5000/api/students/${studentId}/notes`, { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ content: content }) });
        const result = await response.json();
        if (response.ok && result.success) {
            statusSpan.textContent = result.message || "Note saved successfully!"; statusSpan.className = 'message-display success visible'; document.getElementById('note-content').value = '';
            const currentViewingStudentIdForNotes = document.getElementById('view-notes-list')?.getAttribute('data-current-student-id');
            if (currentViewingStudentIdForNotes === studentId) { const dummyButton = document.createElement('button'); dummyButton.setAttribute('data-student-id', studentId); dummyButton.setAttribute('data-student-name', document.querySelector('#add-note-section > p > strong')?.textContent || 'Selected Advisee'); fetchAndDisplayNotesForAdvisee(dummyButton); }
        } else { statusSpan.textContent = result.message || "Failed to save note."; statusSpan.className = 'message-display error visible'; }
    } catch (error) { console.error("Error saving advising note:", error); statusSpan.textContent = "Network error..."; statusSpan.className = 'message-display error visible'; }
}
async function fetchAndDisplayNotesForAdvisee(buttonElement) { /* ... (Keep existing implementation from response #63) ... */ 
    const studentId = buttonElement.getAttribute('data-student-id'); const studentName = buttonElement.getAttribute('data-student-name'); console.log(`Fetching notes for advisee: ${studentName} (ID: ${studentId})`); const token = localStorage.getItem('accessToken'); if (!token) { alert("Authentication token missing."); return; } const notesSection = document.getElementById('view-notes-section'); const notesHeader = document.getElementById('viewing-notes-for-advisee-header'); const notesListUl = document.getElementById('view-notes-list'); const closeNotesButton = document.getElementById('close-advisee-notes-btn');
    if (!notesSection || !notesHeader || !notesListUl || !closeNotesButton) { console.error("One or more UI elements for viewing notes are missing."); return; }
    notesHeader.innerHTML = `Advising Notes for: <strong>${studentName || `Student ID ${studentId}`}</strong>`; notesListUl.innerHTML = '<li><em>Loading notes...</em></li>'; notesListUl.setAttribute('data-current-student-id', studentId); notesSection.style.display = 'block'; closeNotesButton.style.display = 'inline-block'; notesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    try {
        const response = await fetch(`http://localhost:5000/api/students/${studentId}/notes`, { method: 'GET', headers: { 'Authorization': `Bearer ${token}` }});
        if (!response.ok) { let errorMsg = `HTTP error ${response.status}`; try{ const errData = await response.json(); errorMsg = errData.message || errorMsg; } catch(e){} throw new Error(errorMsg); }
        const data = await response.json(); notesListUl.innerHTML = ''; 
        if (data.success && data.notes) {
            if (data.notes.length > 0) {
                data.notes.forEach(note => { const li = document.createElement('li'); li.style.borderBottom = '1px dashed #eee'; li.style.paddingBottom = '10px'; li.style.marginBottom = '10px'; const contentP = document.createElement('p'); contentP.textContent = note.content; contentP.style.marginBottom = '5px'; const metaSpan = document.createElement('span'); metaSpan.style.fontSize = '0.85em'; metaSpan.style.color = '#6c757d'; try { const noteDate = new Date(note.created_at); const dateString = isNaN(noteDate) ? 'Invalid Date' : noteDate.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) + ' ' + noteDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true }); metaSpan.textContent = `By: ${note.author_name || 'Unknown'} on ${dateString}`; } catch (dateError) { metaSpan.textContent = `By: ${note.author_name || 'Unknown'} (timestamp error)`; } li.appendChild(contentP); li.appendChild(metaSpan); notesListUl.appendChild(li); });
            } else { notesListUl.innerHTML = '<li>No advising notes found for this student.</li>'; }
        } else { notesListUl.innerHTML = `<li style="color:red;">${data.message || "Could not retrieve notes."}</li>`; }
    } catch (error) { console.error("Error fetching/displaying advisee notes:", error); notesListUl.innerHTML = `<li style="color:red;">Failed to load notes: ${error.message}</li>`; }
}

function handleFetchError(error) { 
    console.error('Fetch operation failed (in handleFetchError):', error.message); 
    localStorage.clear();
    window.location.href = '../index.html'; 
}
function logoutUser() { 
    console.log("Logout button clicked. Clearing storage and redirecting.");
    localStorage.clear();
    window.location.href = '../index.html'; 
}
