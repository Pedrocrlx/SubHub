
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('container');
    
    const params = new URLSearchParams(window.location.search);
    const signup = params.get('signup')
    if (signup == "true") {
        container.classList.add('active');
    }

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

    const SignUp = params.get('signup')
    if (SignUp == "true") {
        container.classList.add('active');
    }


});

