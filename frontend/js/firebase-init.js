// frontend/js/firebase-init.js
// This script initializes Firebase and handles global authentication state.

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDQikZkdhqvHJGXgPpa1lP88wvlATbX0s0",
    authDomain: "student-advising-system-ff55d.firebaseapp.com",
    projectId: "student-advising-system-ff55d",
    storageBucket: "student-advising-system-ff55d.firebasestorage.app",
    messagingSenderId: "315693881125",
    appId: "1:315693881125:web:647ec16d3ce0449e77accc",
    measurementId: "G-43Q510W9RQ"
};

// Initialize Firebase using the global firebase object from compat libraries
const app = firebase.initializeApp(firebaseConfig);
const analytics = firebase.analytics(); // Initialize analytics
const auth = firebase.auth(); // Initialize Firebase Auth
const db = firebase.firestore(); // Initialize Firestore

// Make auth and db globally accessible for other scripts
window.firebaseApp = app;
window.firebaseAuth = auth;
window.firebaseDb = db;

// Listen for authentication state changes
auth.onAuthStateChanged(async (user) => {
    if (user) {
        // User is signed in.
        console.log("User signed in:", user.uid);
        // Fetch user role from Firestore
        const userDocRef = db.collection('users').doc(user.uid);
        const userDocSnap = await userDocRef.get();

        if (userDocSnap.exists) {
            const userData = userDocSnap.data();
            const role = userData.role;

            localStorage.setItem('firebaseUid', user.uid);
            localStorage.setItem('userEmail', user.email);
            localStorage.setItem('userName', userData.name || user.email);
            localStorage.setItem('userType', role);

            const currentPath = window.location.pathname;
            if (role === 'student' && !currentPath.includes('student/')) {
                window.location.href = 'student/dashboard.html';
            } else if (role === 'lecturer' && !currentPath.includes('lecturer/')) {
                window.location.href = 'lecturer/dashboard.html';
            } else if (!currentPath.includes('student/') && !currentPath.includes('lecturer/') && !currentPath.includes('auth/')) {
                // If on index.html after login, redirect based on role
                if (role === 'student') window.location.href = 'student/dashboard.html';
                else if (role === 'lecturer') window.location.href = 'lecturer/dashboard.html';
            }
            // If already on the correct dashboard or a sub-page, do nothing
        } else {
            console.warn("User document not found in Firestore for UID:", user.uid);
            alert("User profile not found. Please contact support or register if you are a new user.");
            auth.signOut();
        }
    } else {
        // User is signed out.
        console.log("User signed out.");
        localStorage.removeItem('firebaseUid');
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userName');
        localStorage.removeItem('userType');

        const currentPath = window.location.pathname;
        if (!currentPath.includes('index.html') &&
            !currentPath.includes('forgot_password_student.html') &&
            !currentPath.includes('change_password.html')) {
            window.location.href = 'index.html';
        }
    }
});
