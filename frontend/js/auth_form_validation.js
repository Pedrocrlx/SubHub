document.getElementById('signUp').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value.trim();
    const signupEmailErrorMessage = document.getElementById('signup-email-error-message');
    const signupPasswordErrorMessage = document.getElementById('signup-password-error-message');

    signupEmailErrorMessage.textContent = '';
    signupPasswordErrorMessage.textContent = '';

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

    if (!email) {
        signupEmailErrorMessage.textContent = 'Please fill in Email field. ';
        return;
    }
    if (!password) {
        signupPasswordErrorMessage.textContent = 'Please fill in Password field.';
        return;
    }

    if (!emailRegex.test(email)) {
        signupEmailErrorMessage.textContent = 'Invalid email address. Example:name@example.com';
        return;
    }

    if (!passwordRegex.test(password)) {
        signupPasswordErrorMessage.textContent =
            'Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, and one number.';
        return;
    }

    console.log('Login válido:', { email, password });
});
