document.addEventListener("DOMContentLoaded", () => {

});

document.getElementById('signUp').addEventListener('submit', async function (event) {
    event.preventDefault();
     console.log('submit intercepted');
    const username = document.getElementById('signup-username').value.trim();
    const email = document.getElementById('signup-email').value.trim();
    const password = document.getElementById('signup-password').value.trim();
    const signupUsernameErrorMessage = document.getElementById('signup-username-error-message');
    const signupEmailErrorMessage = document.getElementById('signup-email-error-message');
    const signupPasswordErrorMessage = document.getElementById('signup-password-error-message');

    signupUsernameErrorMessage.textContent = '';
    signupEmailErrorMessage.textContent = '';
    signupPasswordErrorMessage.textContent = '';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

    if (!username) {
        signupUsernameErrorMessage.textContent = 'Please fill in Username field.';
        return;
    }
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
    try {
        // Simulate a sign-up process
        // In a real application, you would send the email and password to your server here
        // For example:
        await signUp(username, email, password);
        // Simulating a successful sign-up    
    } catch (error) {
        console.error('Sign up failed:', error);
    };
    Swal.fire({
        title: 'Registered!',
        text: 'Click on the button bellow to Login!',
        icon: 'success',
        confirmButtonText: 'Login!',
        customClass: {
            confirmButton: 'button-primary'
        },
        buttonsStyling: false
    }).then((result) => {
        console.log('Sign up válido:');
        console.log('Login válido:', { email, password });
        window.location.href = 'auth.html';

    });

});

document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    console.log('submit intercepted');
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();
    const loginEmailErrorMessage = document.getElementById('login-email-error-message');
    const loginPasswordErrorMessage = document.getElementById('login-password-error-message');

    loginEmailErrorMessage.textContent = '';
    loginPasswordErrorMessage.textContent = '';

    if (!email) {
        loginEmailErrorMessage.textContent = 'Please fill in Email field.';
        return;
    }
    if (!password) {
        loginPasswordErrorMessage.textContent = 'Please fill in Password field.';
        return;
    }

    try {
        await login(email, password);
        Swal.fire({
            icon: 'success',
            title: 'Login Successful',
            text: 'Welcome back to SubHub!',
            confirmButtonText: 'Continue',
            customClass: {
                confirmButton: 'button-primary'
            },
            buttonsStyling: false
        }).then(() => {
            // Redirect or proceed to dashboard
            console.log('User logged in:', { email });
           window.location.href = 'index.html';
        });

    } catch (error) {
        console.error('incorrect username or password:', error);
        Swal.fire({
            icon: 'error',
            title: 'incorrect username or password',
            text: 'Please double check and try again.',
            confirmButtonText: 'OK',
            customClass: {
                confirmButton: 'button-primary'
            },
            buttonsStyling: false
        });
    };

});

signUp = async (username, email, password) => {
    // Simulate a sign-up process
    // In a real application, you would send the email and password to your server here
    console.log('Sign up successful:', { username, email, password });
}
login = async (email, password) => {
    // Simulate a login process
    // In a real application, you would send the email and password to your server here
    console.log('Login successful:', { email, password });
}


document.querySelectorAll('.floating-input').forEach(input => {
  const update = () => {
    input.classList.toggle('filled', input.value.trim() !== '');
  };
  update();
  // Listen to user typing
  input.addEventListener('input', update);
});
