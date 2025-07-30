// StudentAdvisingSystem/frontend/student/results.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("results.js: DOM loaded. Attempting to load results...");
    loadResults();
});

async function loadResults() {
    const auth = window.firebaseAuth;
    const db = window.firebaseDb;
    const user = auth.currentUser;

    const tableBody = document.querySelector('#results-table tbody');
    if (!tableBody) {
        console.error('Results table body (#results-table tbody) not found.');
        return;
    }
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Loading results...</td></tr>'; // Initial loading message

    if (!user) {
        console.error('results.js: No user logged in. Cannot load results.');
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Authentication required to view results.</td></tr>';
        // Redirection handled by onAuthStateChanged in index.html
        return;
    }

    const studentUid = user.uid;

    try {
        // 1. Fetch results for the current student
        const resultsQuery = db.collection('results')
                               .where('studentId', '==', studentUid)
                               .orderBy('semester', 'desc') // Assuming semester is a string like "2023/2024 - Semester 1" for sorting
                               .get();

        // 2. Fetch all courses (to get course title and units by courseId)
        // This is necessary because Firestore queries cannot join collections directly.
        const coursesQuery = db.collection('courses').get();

        // Run both queries in parallel
        const [resultsSnapshot, coursesSnapshot] = await Promise.all([resultsQuery, coursesQuery]);

        const results = resultsSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        const coursesMap = {};
        coursesSnapshot.docs.forEach(doc => {
            coursesMap[doc.id] = doc.data();
        });

        console.log("results.js: Fetched results:", results);
        console.log("results.js: Fetched courses map:", coursesMap);

        if (results.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No official academic results found.</td></tr>';
        } else {
            tableBody.innerHTML = ''; // Clear loading message
            results.forEach(r => {
                const course = coursesMap[r.courseId]; // Get course details using courseId
                let row = tableBody.insertRow();

                row.insertCell(0).innerText = course?.code || 'N/A';
                row.insertCell(1).innerText = course?.title || 'N/A';
                row.insertCell(2).innerText = course?.units !== null && course?.units !== undefined ? course.units : 'N/A';
                row.insertCell(3).innerText = r.semester || 'N/A';
                row.insertCell(4).innerText = r.grade || 'N/A';
                row.insertCell(5).innerText = r.gpa !== null && r.gpa !== undefined ? parseFloat(r.gpa).toFixed(2) : 'N/A';
            });
        }
    } catch (error) {
        console.error('results.js: Error fetching results from Firestore:', error);
        let errorMessage = 'Failed to load results. Please check your connection or try again.';
        if (error.code === 'permission-denied') {
            errorMessage = 'You do not have permission to view these results.';
        } else if (error.code === 'unavailable') {
            errorMessage = 'Firestore is currently unavailable. Please try again later.';
        }
        tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red;">${errorMessage}</td></tr>`;
        // Potentially redirect to login if it's an auth error
        if (error.code === 'permission-denied' || error.code === 'unauthenticated') {
            await auth.signOut();
        }
    }
}
