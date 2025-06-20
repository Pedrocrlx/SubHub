document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        window.location.href = "/auth/";
        return;
    }

    // Obter info do utilizador (nome/email)
    const userName = localStorage.getItem("user_name");
    const userEmail = localStorage.getItem("user_email");

    // Atualizar DOM com o nome
    const userDisplay = document.getElementById("user-info");
    if (userDisplay && userName) {
        userDisplay.textContent = `Welcome, ${userName}!`;
    }

    // Exemplo de fetch autenticado
    fetch("http://localhost:8000/subscriptions", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .then(data => {
        console.log("Subscrições:", data);
        // Aqui podes atualizar o DOM com os dados
    })
    .catch(err => {
        console.error("Erro ao buscar subscrições:", err);
        if (err.message === "Unauthorized") {
            localStorage.clear();
            window.location.href = "/auth/";
        }
    });
});

document.getElementById("logout-btn").addEventListener("click", () => {
    const token = localStorage.getItem("access_token");

    fetch("http://localhost:8000/logout", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
    .finally(() => {
        localStorage.clear();
        window.location.href = "auth.html";
    });
});
