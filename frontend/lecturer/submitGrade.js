// StudentAdvisingSystem/frontend/lecturer/submitGrade.js
document.addEventListener('DOMContentLoaded', () => {
    console.log("Submit Grade DOM loaded.");

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
        applyCurrentTheme(); // Apply theme on initial load

        themeToggleButton.addEventListener('click', () => {
            bodyElement.classList.toggle('dark-mode');
            let newTheme = bodyElement.classList.contains('dark-mode') ? 'dark' : 'light';
            themeToggleButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
            localStorage.setItem('theme', newTheme);
            console.log("Theme toggled on Submit Grade page to:", newTheme);
        });
    } else {
        if (!themeToggleButton) console.warn("Theme toggle button (#theme-toggle-button) not found on Submit Grade page.");
        if (!bodyElement) console.warn("Body element not found for theme toggle on Submit Grade page.");
    }
    // --- END THEME TOGGLE LOGIC ---

    // --- EXISTING SUBMIT GRADE FORM LOGIC ---
    const submitGradeForm = document.getElementById('submitGradeForm');
    const messageArea = document.getElementById('submit-grade-message');

    if (!submitGradeForm) {
        console.error("Submit grade form (#submitGradeForm) not found!");
        if(messageArea) messageArea.textContent = "Form error. Please contact support.";
        return;
    }
    if (!messageArea) {
        console.warn("Message area (#submit-grade-message) not found. Alerts will be used for feedback.");
    }

    submitGradeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (messageArea) {
            messageArea.textContent = 'Processing...';
            messageArea.className = 'message-display visible'; // Use classes for styling
            messageArea.style.color = ''; // Reset direct style
        }

        const token = localStorage.getItem('accessToken');
        if (!token) {
            const msg = 'Authentication error. Please log in again.';
            if (messageArea) {
                messageArea.textContent = msg;
                messageArea.className = 'message-display error visible';
            } else { alert(msg); }
            // Consider redirecting after a delay: setTimeout(() => window.location.href = '../index.html', 2000);
            return;
        }

        const studentIdValue = document.getElementById('studentId').value;
        const courseIdValue = document.getElementById('courseId').value;
        const gradeValue = document.getElementById('grade').value;
        const semesterValue = document.getElementById('semester').value;
        const gpaValue = document.getElementById('gpa').value; // GPA field is not 'required' in HTML

        // Basic frontend validation (backend does more thorough validation)
        if (!studentIdValue || !courseIdValue || !gradeValue || !semesterValue) {
            const msg = 'Student ID, Course ID, Grade, and Semester are required.';
            if (messageArea) {
                messageArea.textContent = msg;
                messageArea.className = 'message-display error visible';
            } else { alert(msg); }
            return;
        }
        // GPA can be optional, but if provided, it should be a number
        let gpaFloat = null;
        if (gpaValue.trim() !== "") { // Only parse if not empty
            gpaFloat = parseFloat(gpaValue);
            if (isNaN(gpaFloat)) {
                const msg = 'Grade Points (GPA) must be a valid number if provided.';
                if (messageArea) {
                    messageArea.textContent = msg;
                    messageArea.className = 'message-display error visible';
                } else { alert(msg); }
                return;
            }
        }


        const payload = {
            student_id: studentIdValue,
            course_id: courseIdValue,
            grade: gradeValue,
            semester: semesterValue,
            gpa: gpaFloat // Send null if gpaValue was empty, or the float value
        };

        console.log("Submitting grade with payload:", payload);

        try {
            const response = await fetch('http://localhost:5000/api/lecturer/submit-grade', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            console.log("Submit grade API response status:", response.status, "Response JSON:", result);

            if (response.ok && result.success) {
                if (messageArea) {
                    messageArea.textContent = result.message || 'Grade submitted successfully!';
                    messageArea.className = 'message-display success visible';
                } else {
                    alert(result.message || 'Grade submitted successfully!');
                }
                submitGradeForm.reset();
            } else {
                const errorMessage = result.message || `Error: ${response.statusText || 'Failed to submit grade.'}`;
                if (messageArea) {
                    messageArea.textContent = errorMessage;
                    messageArea.className = 'message-display error visible';
                } else {
                    alert(errorMessage);
                }
            }
        } catch (error) {
            console.error('Error submitting grade (network or parsing error):', error);
            if (messageArea) {
                messageArea.textContent = 'Network error or failed to connect to the server.';
                messageArea.className = 'message-display error visible';
            } else {
                alert('Network error or failed to connect to the server.');
            }
        }
    });
});