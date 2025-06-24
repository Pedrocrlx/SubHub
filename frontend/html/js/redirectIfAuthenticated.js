document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");

    // Se estiver autenticado, redirecionar para o dashboard
    if (token) {
        window.location.href = "/dashboard/";
    }
});
