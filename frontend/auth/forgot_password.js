// StudentAdvisingSystem/frontend/auth/forgot_password.js
document.addEventListener('DOMContentLoaded', () => {
    // Get references to the form elements from forgot_password_student.html
    const forgotPasswordForm = document.getElementById('forgot-password-student-form');
    const matricNumberInput = document.getElementById('matric-number');
    const messageArea = document.getElementById('message-area');

    if (!forgotPasswordForm) {
        console.warn("Forgot password form ('#forgot-password-student-form') not found by forgot_password.js.");
        return;
    }
    if (!matricNumberInput) {
        console.warn("Matric number input ('#matric-number') not found by forgot_password.js.");
        // If the form exists but not this input, the script can't function.
        if (messageArea) messageArea.textContent = "Form input error. Please contact support.";
        return;
    }
    if (!messageArea) {
        console.warn("Message area ('#message-area') not found by forgot_password.js. Alerts will be used.");
    }

    forgotPasswordForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        if (messageArea) {
            messageArea.textContent = 'Processing...';
            messageArea.style.color = '#6c757d'; // Neutral color (consider CSS variables)
        } else {
            // Fallback if messageArea isn't there for some reason
        }

        const matricNumber = matricNumberInput.value.trim();

        if (!matricNumber) {
            if (messageArea) {
                messageArea.textContent = 'Please enter your Matric Number.';
                messageArea.style.color = 'red'; // Error color (consider CSS variables)
            } else {
                alert('Please enter your Matric Number.');
            }
            return;
        }

        const apiUrl = 'http://localhost:5000/api/students/forgot-password'; // Ensure your backend has this
        const payload = {
            matric_number: matricNumber
        };

        console.log("Sending password reset request for student matric_number:", payload.matric_number);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json(); // Attempt to parse JSON for all responses
            console.log("Backend response to forgot password:", result);

            if (response.ok && result.success) { // Check for HTTP OK and your backend's success flag
                if (messageArea) {
                    messageArea.textContent = result.message || 'Password reset instructions sent successfully.';
                    messageArea.style.color = 'green'; // Success color (consider CSS variables)
                } else {
                    alert(result.message || 'Password reset instructions sent successfully.');
                }
                matricNumberInput.value = ''; // Clear the input field on success
            } else {
                if (messageArea) {
                    messageArea.textContent = result.message || `Error: ${response.statusText || 'Failed to send reset email.'}`;
                    messageArea.style.color = 'red';
                } else {
                    alert(result.message || `Error: ${response.statusText || 'Failed to send reset email.'}`);
                }
            }

        } catch (error) {
            console.error("Network error requesting password reset:", error);
            if (messageArea) {
                messageArea.textContent = 'A network error occurred. Please check your connection and try again.';
                messageArea.style.color = 'red';
            } else {
                alert('A network error occurred. Please check your connection and try again.');
            }
        }
    });
});