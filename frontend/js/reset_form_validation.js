import { resetPassword, email_send_validation } from "./resetPassword.js";
document.addEventListener("DOMContentLoaded", () => {

});

document.getElementById('reset-email-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    console.log('submit intercepted');
    const email = document.getElementById('reset-email').value.trim();
    const resetEmailErrorMessage = document.getElementById('reset-email-error-message');

    resetEmailErrorMessage.textContent = '';
    if (!email) {
        resetEmailErrorMessage.textContent = 'Please fill in Email field. ';
        return;
    }
    else {
        try {
            window.location.href = 'resetPassword.html?verified=true&email=' + email;
            //await email_send_validation(email);
        } catch (error) {
            console.error('couldnt send email to reset the password:', error);
        };
        Swal.fire({
            title: 'Link sent to your email!',
            text: 'Please verify your email to reset your password.',
            icon: 'success'
        });
    }

});

document.getElementById('reset-password-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    console.log('submit intercepted');
    const password = document.getElementById('reset-password').value.trim();
    const passwordRepeat = document.getElementById('reset-password-repeat').value.trim();
    const resetPasswordErrorMessage = document.getElementById('reset-password-error-message');
    const resetPasswordRepeatErrorMessage = document.getElementById('reset-password-repeat-error-message');

    resetPasswordErrorMessage.textContent = '';
    resetPasswordRepeatErrorMessage.textContent = '';


    if (!password) {
        resetPasswordErrorMessage.textContent = 'Please fill in password field.';
        return;
    }
    if (!passwordRepeat) {
        resetPasswordRepeatErrorMessage.textContent = 'Please fill in password repeat field.';
        return;
    }
    if (password !== passwordRepeat) {
        resetPasswordRepeatErrorMessage.textContent = 'Passwords do not match.';
        return;
    }
    else {
        try {
            await resetPassword(password);

        } catch (error) {
            console.error('error: ', error);
            Swal.fire({
                icon: 'error',
                title: 'ERROR',
                text: 'couldnt reset your password at the moment try again',
                confirmButtonText: 'OK',
                customClass: {
                    confirmButton: 'button-primary'
                },
                buttonsStyling: false
            });
        };
    }

});

document.querySelectorAll('.floating-input').forEach(input => {
  const update = () => {
    input.classList.toggle('filled', input.value.trim() !== '');
  };
  update();
  // Listen to user typing
  input.addEventListener('input', update);
});