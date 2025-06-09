document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById('container');

  // Pega os parâmetros da URL
  const params = new URLSearchParams(window.location.search);
  const token = params.get('token');
  const email = params.get('email');
  const verified = params.get('verified')
  if (verified === "true") {
    container.classList.add('active');
  } else {
    container.classList.remove('active');
  }
  if (verified && verified != "true") {
    window.location.href = "auth.html";
    container.classList.remove('active');
  }

});

function login(){
  window.location.href = "auth.html";
}

// Exemplo: exibe no status (apenas para debug, remover depois)
document.getElementById("status").textContent =
  token && email ? `Token: ${token}, Email: ${email}` : 'Parâmetros inválidos';

// Se quiser lidar com o envio do form
const form = document.getElementById('resetForm');
form.addEventListener('submit', function (e) {
  e.preventDefault();
  const newPassword = document.getElementById('newPassword').value;

  // Aqui você faria uma chamada para sua API para redefinir a senha
  // Exemplo de fetch:
  fetch('https://api.teusite.com/reset-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      token: token,
      email: email,
      newPassword: newPassword
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Senha redefinida com sucesso!');
        // Redirecionar para login ou outra página
      } else {
        alert('Erro ao redefinir a senha.');
      }
    })
    .catch(err => {
      console.error('Erro na requisição:', err);
      alert('Erro ao redefinir a senha.');
    });
});