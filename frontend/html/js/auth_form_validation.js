
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
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d])[A-Za-z\d\W]{8,}$/;

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
            'Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, one number and one symbol.';
        return;
    }
    try {
        await registerUser(username, email, password);
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
            window.location.href = '/auth/';

        });
    } catch (error) {
        console.error('Sign up failed:', error);
        Swal.fire({
            icon: 'error',
            title: 'Sign up Failed',
            text: 'Please try again later.',
            confirmButtonText: 'OK',
            customClass: {
                confirmButton: 'button-primary'
            },
            buttonsStyling: false
        }); 
    };

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
            console.log('User logged in:', { email });
            window.location.href = '/dashboard/';
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

const registerUser = async (username, email, password) => {
    try {
        console.log("Dados sendo enviados:", { username, email, password });

        const response = await fetch('http://localhost:8000/register', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,  // Certifique-se de que o campo é 'name' (ou ajuste para o esperado pelo backend)
                email: email,
                password: password,
            }),
            credentials: "include",  // Opcional: só use se o backend exigir cookies/sessão
        });

        console.log("Resposta do servidor:", response);

        if (!response.ok) {
            // Tenta extrair a mensagem de erro do JSON (se o backend retornar JSON)
            const errorData = await response.json().catch(() => null);
            const errorMessage = errorData?.detail || "Erro desconhecido";
            Swal.fire({
                icon: 'error',
                title: errorMessage,
                text: 'Please try again later.',
                confirmButtonText: 'OK',
                customClass: {
                    confirmButton: 'button-primary'
                },
                buttonsStyling: false
            });
            throw new Error(`Falha no registro: ${errorMessage} (Status: ${response.status})`);
        }

        const data = await response.json();
        console.log("Registro bem-sucedido:", data);
        return data;  // Retorna os dados do usuário (opcional)

    } catch (error) {
        console.error("Erro durante o registro:", error.message);
        throw error;  // Propaga o erro para ser tratado pelo chamador
    }
};

const login = async (email, password) => {
    const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
    }

    const data = await response.json();

    // Guardar no localStorage
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user_name", data.user_name);
    localStorage.setItem("user_email", data.user_email);

    console.log('Login successful:', data);
};


document.querySelectorAll('.floating-input').forEach(input => {
    const update = () => {
        input.classList.toggle('filled', input.value.trim() !== '');
    };
    update();
    // Listen to user typing
    input.addEventListener('input', update);
});
