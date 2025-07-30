// frontend/student/profile.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("Student Profile DOM loaded.");

    // Fetch profile data using Firebase
    fetchStudentProfileData();
});

async function fetchStudentProfileData() {
    console.log("Fetching student profile data from Firestore...");
    const auth = window.firebaseAuth;
    const db = window.firebaseDb;
    const user = auth.currentUser;

    if (!user) {
        console.error("No user logged in. Redirecting to login.");
        // Redirection handled by onAuthStateChanged in index.html
        return;
    }

    const studentUid = user.uid;
    const profileDetailsCard = document.getElementById('profile-details-card');

    try {
        const studentDocRef = db.collection('users').doc(studentUid);
        const studentDocSnap = await studentDocRef.get();

        if (studentDocSnap.exists) {
            const studentData = studentDocSnap.data();
            console.log("Student Profile Data from Firestore:", studentData);
            populateStudentProfilePage(studentData);

            // Fetch advisor info if advisorId exists
            if (studentData.advisorId) {
                const advisorDocRef = db.collection('users').doc(studentData.advisorId);
                const advisorDocSnap = await advisorDocRef.get();
                if (advisorDocSnap.exists) {
                    const advisorData = advisorDocSnap.data();
                    console.log("Advisor Profile Data from Firestore:", advisorData);
                    populateAdvisorProfileInfo(advisorData);
                } else {
                    console.warn("Advisor document not found for ID:", studentData.advisorId);
                    setTextContent('profile-advisor-name', 'Not Assigned / Profile Missing');
                    setTextContent('profile-advisor-email', '');
                    setTextContent('profile-advisor-dept', '');
                    setTextContent('profile-advisor-office', '');
                }
            } else {
                setTextContent('profile-advisor-name', 'Not Assigned');
                setTextContent('profile-advisor-email', '');
                setTextContent('profile-advisor-dept', '');
                setTextContent('profile-advisor-office', '');
            }

        } else {
            console.error("Student document not found in Firestore for UID:", studentUid);
            if (profileDetailsCard) {
                profileDetailsCard.innerHTML = `<p class="error-message">Your student profile could not be loaded. Please contact support.</p>`;
            }
            await auth.signOut(); // Sign out if profile doesn't exist
        }
    } catch (error) {
        console.error("Error fetching student profile data:", error);
        if (profileDetailsCard) {
            profileDetailsCard.innerHTML = `<p class="error-message">Failed to load profile data. Please check your internet connection or try again later.</p>`;
        }
        // Potentially redirect to login if it's an auth error
        if (error.code === 'permission-denied' || error.code === 'unauthenticated') {
            await auth.signOut();
        }
    }
}

function populateStudentProfilePage(studentInfo) {
    setTextContent('profile-fullname', studentInfo.name || 'N/A');
    setTextContent('profile-matric-number', studentInfo.matric_number || 'N/A');
    setTextContent('profile-email', studentInfo.email || 'N/A');
    setTextContent('profile-dob', studentInfo.dob || 'N/A'); // Date of Birth
    setTextContent('profile-gender', studentInfo.gender || 'N/A');
    setTextContent('profile-phone', studentInfo.phone_number || 'N/A');
    setTextContent('profile-address', studentInfo.address || 'N/A');

    // Academic Info
    setTextContent('profile-degree', studentInfo.degree?.name || 'Not Assigned');
    setTextContent('profile-faculty', studentInfo.degree?.faculty || 'N/A'); // Assuming degree object has faculty
    setTextContent('profile-overall-gpa', studentInfo.gpa !== null && studentInfo.gpa !== undefined ? studentInfo.gpa.toFixed(2) : 'N/A');

    // Guardian Info
    setTextContent('profile-guardian-name', studentInfo.guardian_name || 'N/A');
    setTextContent('profile-guardian-email', studentInfo.guardian_email || 'N/A');
    setTextContent('profile-guardian-phone', studentInfo.guardian_phone || 'N/A');
    setTextContent('profile-guardian-relationship', studentInfo.guardian_relationship || 'N/A');

    console.log("Student profile page populated.");
}

function populateAdvisorProfileInfo(advisorInfo) {
    setTextContent('profile-advisor-name', advisorInfo.name || 'N/A');
    setTextContent('profile-advisor-email', advisorInfo.email || 'N/A');
    setTextContent('profile-advisor-dept', advisorInfo.department || 'N/A');
    setTextContent('profile-advisor-office', advisorInfo.office_location || 'N/A');
}

function setTextContent(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = (text === null || text === undefined) ? '' : String(text);
    } else {
        // console.warn(`Element with ID '${elementId}' not found for setTextContent.`);
    }
}
