
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('container');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    if (registerBtn) {
        registerBtn.addEventListener('click', () => {
            console.log('Register button clicked');
            container.classList.add('active');
        });

    }
    loginBtn.addEventListener('click', () => {
        container.classList.remove('active');
    });

});
