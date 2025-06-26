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


export async function email_send_validation(email) {
// Aqui você faria uma chamada para sua API para enviar o email de validação
  // Exemplo de fetch:
  fetch('https://api.teusite.com/send-reset-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Email de redefinição enviado com sucesso!');
        // Redirecionar para a página de redefinição de senha
      } else {
        alert('Erro ao enviar o email de redefinição.');
      }
    })
    .catch(err => {
      console.error('Erro na requisição:', err);
      alert('Erro ao enviar o email de redefinição.');
    });
}

export async function resetPassword(newPassword) {

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
}